##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Globals import InitializeClass, Persistent, Acquisition
from Acquisition import aq_base, aq_inner, aq_parent, aq_self
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.PythonScripts.Utility import allow_class
import string

# Put a try in front XXX
from Products.CMFCategory.Category import Category
from Products.ERP5.Document.Domain import Domain

from zLOG import LOG

class Selection(Acquisition.Implicit, Traversable, Persistent):
    """
        Selection

        A Selection instance allows a ListBox object to browse the data
        resulting from a method call such as an SQL Method Call. Selection
        instances are used to implement persistent selections in ERP5.

        Selection uses the following control variables

        - method      --  a method which will be used
                                    to select objects

        - params      --  a dictionnary of parameters to call the
                                    method with

        - sort_on     --  a dictionnary of parameters to sort
                                    the selection

        - uids        --  a list of object uids which defines the
                                    selection

        - invert_mode --  defines the mode of the selection
                                    if mode is 1, then only show the
                                    ob

        - list_url    --  the URL to go back to list mode

        - checked_uids --  a list of uids checked

        - domain_path --  the path to the root of the selection tree


        - domain_list --  the relative path of the current selected domain
                                    XXX this will have to be updated for cartesion product

        - report_path --  the report path

        - report_list -- list of open report nodes
                                    XXX this will have to be updated for cartesion product

        - domain                -- a DomainSelection instance

        - report                -- a DomainSelection instance

        - flat_list_mode  --

        - domain_tree_mode --

        - report_tree_mode --

    """

    method_path=None
    params={}
    sort_on=()
    default_sort_on=None
    uids=()
    invert_mode=0
    list_url=''
    columns=()
    checked_uids=()
    name=None
    index=None
    domain_path = ('portal_categories',)
    domain_list = ((),)
    report_path = ('portal_categories',)
    report_list = ((),)
    domain=None
    report=None

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    security.declarePublic('domain')
    security.declarePublic('report')

    def __init__(self, method_path=None, params=None, sort_on=None, default_sort_on=None,
                 uids=None, invert_mode=0, list_url='', domain=None, report=None,
                 columns=None, checked_uids=None, name=None, index=None):
        if params is None: params = {}
        if sort_on is None: sort_on = []
        if uids is None: uids = []
        if columns is None: columns = []
        if checked_uids is None: checked_uids = []
        # XXX Because method_path is an URI, it must be in ASCII.
        #     Shouldn't Zope automatically does this conversion? -yo
        if type(method_path) is type(u'a'):
          method_path = method_path.encode('ascii')
        self.method_path = method_path
        self.params = params
        self.uids = uids
        self.invert_mode = invert_mode
        self.list_url = list_url
        self.columns = columns
        self.sort_on = sort_on
        self.default_sort_on = default_sort_on
        self.checked_uids = checked_uids
        self.name = name
        self.index = index
        self.domain_path = ('portal_categories',)
        self.domain_list = ()
        self.report_path = ('portal_categories',)
        self.report_list = ()
        self.domain = None
        self.report = None

    security.declarePrivate('edit')
    def edit(self, params=None, **kw):
        if params is not None:
          self.params = {}
          for key in params.keys():
            # We should only keep params which do not start with field_
            # in order to make sure we do not collect unwanted params
            # resulting form the REQUEST generated by an ERP5Form submit
            if key[0:6] != 'field_':
              self.params[key] = params[key]
        if kw is not None:
          for k,v in kw.items():
            if k in ('domain', 'report') or v is not None:
              # XXX Because method_path is an URI, it must be in ASCII.
              #     Shouldn't Zope automatically does this conversion? -yo
              if k == 'method_path' and type(v) is type(u'a'):
                v = v.encode('ascii')
              setattr(self, k, v)

    def __call__(self, method = None, context=None, REQUEST=None):
        #LOG("Selection", 0, str(self.__dict__))
        #LOG("Selection", 0, str(method))
        #LOG('Selection', 0, "self.invert_mode = %s" % repr(self.invert_mode))
        if self.invert_mode is 0:
          if method is None:
            method = context.unrestrictedTraverse(self.method_path)
          sort_on = getattr(self, 'sort_on', [])
          if len(sort_on) == 0:
            sort_on = getattr(self, 'default_sort_on', [])
          if len(sort_on) > 0:
            new_sort_index = []
            for (k , v) in sort_on:
              if v == 'descending' or v == 'reverse':
                new_sort_index += ['%s DESC' % k]
              else:
                new_sort_index += ['%s' % k]
            sort_order_string = string.join(new_sort_index,',')
            self.params['sort_on'] = sort_order_string
          elif self.params.has_key('sort_on'):
            del self.params['sort_on']
          if method is not None:
            if callable(method):
              #LOG('Selection', 0, "self.params = %s" % repr(self.params))
              if self.domain is not None and self.report is not None:
                result = method(selection_domain = self.domain,
                                selection_report = self.report, selection=self, **self.params)
              elif self.domain is not None:
                result = method(selection_domain = self.domain, selection=self, **self.params)
              elif self.report is not None:
                result = method(selection_report = self.report, selection=self, **self.params)
              else:
                result = method(selection=self, **self.params)
              return result
            else:
              return []
          else:
            return []
        else:
          # We sould try to allow more filtering
          return context.portal_catalog(uid = self.uids)

    def __getitem__(self, index, REQUEST=None):
        return self(REQUEST)[index]

    security.declarePublic('getName')
    def getName(self):
        """
          Get the name of this selection.
        """
        return self.name

    security.declarePublic('getIndex')
    def getIndex(self):
        """
          Get the index of this selection.
        """
        return self.index

    security.declarePublic('getDomain')
    def getDomain(self):
        """
          Get the domain selection of this selection.
        """
        return self.domain

    security.declarePublic('getParams')
    def getParams(self):
        """
          Get a dictionary of parameters in this selection.
        """
        LOG('getParams',0,'params: %s' % str(self.params))
        if self.params is None:
          self.params = {}
        if type(self.params) != type({}):
          self.params = {}
        return self.params

    security.declarePublic('getListUrl')
    def getListUrl(self):
        result = ''
        LOG('getListUrl', 0, 'list_url = %s' % str(self.list_url))
        if self.list_url is None:
          self.list_url = ''
        else:
          result = self.list_url
        return result

    security.declarePublic('getCheckedUids')
    def getCheckedUids(self):
        if not hasattr(self, 'checked_uids'):
          self.checked_uids = []
        elif self.checked_uids is None:
          self.checked_uids = []
        return self.checked_uids

    security.declarePublic('getDomainPath')
    def getDomainPath(self):
        if self.domain_path is None:
          self.domain_path = self.getDomainList()[0]
        return self.domain_path

    security.declarePublic('getDomainList')
    def getDomainList(self):
        if self.domain_list is None:
          self.domain_list = (('portal_categories',),)
        return self.domain_list

    security.declarePublic('getReportPath')
    def getReportPath(self):
        if self.report_path is None:
          self.report_path = ('portal_categories')
        return self.report_path

    security.declarePublic('getReportList')
    def getReportList(self):
        if self.report_list is None:
          self.report_list = (('portal_categories',),)
        return self.report_list

InitializeClass(Selection)
allow_class(Selection)

class DomainSelection(Acquisition.Implicit, Traversable, Persistent):
  """
    A class to store a selection of domains which defines a report
    section.

    Example 1: (hand coded)

    <dtml-if selection.domain.eip>
      <dtml-in "selection.domain.eip.getCategoryChildUidList()">uid = <dtml-sqlvar sequence-item type="int"></dtml-in>
    </dtml-if>

    Example 2: (auto generated)

    <dtml-var "selection.domain.asSqlExpression(table_map=(('eip','movement'), ('group', 'catalog')))">
    <dtml-var "selection.domain.asSqlJoinExpression(table_map=(('eip','movement'), ('group', 'catalog')))">

    Example 3: (mixed)

    <dtml-var "selection.domain.eip.asSqlExpresion(table="resource_category")">

  """

  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def __init__(self, domain_dict = None):
    if domain_dict is not None:
      self.domain_dict = domain_dict
      for k,v in domain_dict.items():
        if k is not None:
          setattr(self, k, v)

  def __len__(self):
    return len(self.domain_dict)

  security.declarePublic('getCategoryList')
  def getCategoryList(self):
    return

  security.declarePublic('asSqlExpression')
  def asSqlExpression(self, table_map=None, domain_id=None, exclude_domain_id=None, strict_membership=0):
    join_expression = []
    for k, d in self.domain_dict.items():
      if k is not None and getattr(aq_base(d), 'isCategory', 0):
        # This is a category, we must join
        join_expression.append('catalog.uid = %s_category.uid' % k)
        join_expression.append(d.asSqlExpression(table = '%s_category' % k, strict_membership=strict_membership))
    result = "( %s )" % ' AND '.join(join_expression)
    LOG('asSqlExpression', 0, str(result))
    return result

  security.declarePublic('asSqlJoinExpression')
  def asSqlJoinExpression(self, domain_id=None, exclude_domain_id=None):
    join_expression = []
    for k, d in self.domain_dict.items():
      if k is not None and getattr(aq_base(d), 'isCategory', 0):
        # This is a category, we must join
        join_expression.append('category AS %s_category' % k)
    result = "%s" % ' , '.join(join_expression)
    LOG('asSqlJoinExpression', 0, str(result))
    return result

  security.declarePublic('asDomainDict')
  def asDomainDict(self, domain_id=None, exclude_domain_id=None):
    pass

  security.declarePublic('asDomainItemDict')
  def asDomainItemDict(self, domain_id=None, exclude_domain_id=None):
    pass

  security.declarePublic('updateDomain')
  def updateDomain(self, domain):
    pass

InitializeClass(DomainSelection)
allow_class(DomainSelection)
