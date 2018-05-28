# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

import deepdiff
import difflib
from deepdiff import DeepDiff
from unidiff import PatchSet
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import interfaces
from Products.PythonScripts.PythonScript import PythonScript

class DiffTool(BaseTool):
  """
  A portal tool that provides all kinds of utilities to
  compare objects.
  """
  id = 'portal_diff'
  title = 'Diff Tool'
  meta_type = 'ERP5 Diff Tool'
  portal_type = 'Diff Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'diffPortalObject')
  def diffPortalObject(self, old_value, new_value, path=None, patch_format="deepdiff"):
    """
      Returns a PortalPatch instance with the appropriate format
      path -- optional path to specify which property to diff
      patch_format -- optional format (rfc6902 or deepdiff)
    """
    return PortalPatch(old_value, new_value, path, patch_format)

  security.declarePrivate('patchPortalObject')
  def patchPortalObject(self, old, diff_list):
    """
    Receives the dict with old object, diff value and returns a new object from
    the diff and the old value
    """

    copy_data = old.aq_parent.manage_copyObjects([old.id,])
    new_id = old.aq_parent.manage_pasteObjects(copy_data)[0]['new_id']
    new_obj = old.aq_parent[new_id]

    for diff in diff_list:
      setattr(new_obj, diff['path'], diff['t2'])

    return new_obj

class PortalPatch:
  """
    Provides an abstraction to a patch that
    depends on the patch format.

    In the case of deepdiff, the abstraction can
    lead to a commutative merge system.

    In the case of rfc6902, the abstraction can not
    lead to a commutative merge system but may be
    useful to some UI applications.
  """

  # Declarative Security
  security = ClassSecurityInfo()

  def __init__(self, old_value, new_value, path=None, patch_format="deepdiff"):
    """
    Intialises the class from a deepdiff or
    a rfc6902 patch. deepdiff is the default.

    old_value -- Old Value (can be an object, dict, string or other object type)
                 which we want to compare the changes from
    new_value -- New Value which we want to see what has been changed from old
                 value
    """
    self.old_value = old_value
    self.new_value = new_value
    self.patch_format = patch_format

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asBeautifiedJSONDiff')
  def asBeautifiedJSONDiff(self):
    """
    Returns beautified JSON diff in format:
    {
    'diff': <diff>
    't1': <old_value>
    't2': <new_value>
    'path', <property_name>
    }
    """
    old_value_dict = self.removePropertyList(self.old_value, export=True)
    new_value_dict = self.removePropertyList(self.new_value, export=True)

    # Get the DeepDiff in tree format.
    tree_diff = DeepDiff(old_value_dict,
                         new_value_dict,
                         view='tree')
    diff_tree_list = []

    # Flatten the list of DiffValues
    for key, subset in tree_diff.items():
      if isinstance(subset, set):
        sublist = list(subset)
        for item in sublist:
          # XXX: This is important as the subsets with iterable item removed
          # do always have items which are diffing the items in list and not the
          # complete list, hence we get paths as root[<list_name>][<index_no>]
          # which is inconsistent to manage in string formatting, thus we have
          # decided to use the parent list by using .up
          if key in ('iterable_item_removed',):
            diff_tree_list.append(item.up)
          else:
            diff_tree_list.append(item)

    # Create a beautified list from the diff
    diff_list = []
    for val in diff_tree_list:
      new_val = {}

      diff = val.additional.get('diff', None)
      # If there is diff in additional property, save it separately
      if diff:
        # Add space in front of each newline character as it validates the diff
        diff = diff.replace('\n', ' \n')

        patch = PatchSet(diff)
        # Get the 1st item from the PatchSet which is the patch object
        patch = patch[0]
        # In case there are multiple hunks, do create separate value dict for
        # each of them
        for l in patch:
          new_val = {}
          # Add the headers on top of every patch as they are needed for
          # rendering as pretty HTML
          new_val['diff'] = "---  \n+++  \n" + str(l)
          new_val['t1'] = val.t1
          new_val['t2'] = val.t2
          new_val['path'] = val.path()[6:-2]
          diff_list.append(new_val)
      else:
        old_value = val.t1
        new_value = val.t2
        if (val.t1 == None) or isinstance(val.t1, deepdiff.helper.NotPresent):
          old_value = ''
        if (val.t2 == None) or isinstance(val.t2, deepdiff.helper.NotPresent):
          new_value = ''

        try:
          # Create unified diff for single string cases
          new_val['diff'] = ''.join(difflib.unified_diff([str(old_value)+'\n'], [str(new_value)+'\n'])).replace('\n', ' \n')
        except ValueError:
          # Show empty diff in case of error in new or old value type
          new_val['diff'] = None
        new_val['path'] = val.path()[6:-2]
        new_val['t1'] = val.t1
        new_val['t2'] = val.t2

        diff_list.append(new_val)

    # Sort the list of dictionaries according to the path
    sorted_diff_list = sorted(diff_list, key=lambda k: k['path'])

    return sorted_diff_list

  security.declarePrivate('removePropertyList')
  def removePropertyList(self,
                       obj,
                       export,
                       property_list=None,
                       keep_workflow_history=False,
                       keep_workflow_history_last_history_only=False):
    """
    This function removes un-necessary properties and attributes from the
    object dict.
    """
    if isinstance(obj, dict):
      obj_dict = obj.copy()
      export = False
    else:
      obj._p_activate()
      klass = obj.__class__
      classname = klass.__name__
      obj_dict = obj.showDict().copy()

    attribute_set = {'_dav_writelocks', '_filepath', '_owner', '_related_index',
                     'last_id', 'uid', '_mt_index', '_count', '_tree',
                     '__ac_local_roles__', '__ac_local_roles_group_id_dict__',
                     'workflow_history', 'subject_set_uid_dict', 'security_uid_dict',
                     'filter_dict', '_max_uid', 'isIndexable', 'id', 'modification_date',
                     'data'}

    # Update the list of properties which were explicitly given in parameters
    if property_list:
      for prop in property_list:
        if prop.endswith('_list'):
          prop = prop[:-5]
        attribute_set.add(prop)

    if export:
      if keep_workflow_history_last_history_only:
        self._removeAllButLastWorkflowHistory(obj)
      elif not keep_workflow_history:
        attribute_set.add('workflow_history')
      # PythonScript covers both Zope Python scripts
      # and ERP5 Python Scripts
      if isinstance(obj, PythonScript):
        attribute_set.update(('func_code', 'func_defaults', '_code',
                         '_lazy_compilation', 'Python_magic', 'errors',
                         'warnings', '_proxy_roles'))
      elif classname in ('File', 'Image'):
        attribute_set.update(('_EtagSupport__etag', 'size'))
      elif classname == 'SQL' and klass.__module__ == 'Products.ZSQLMethods.SQL':
        attribute_set.update(('_arg', 'template'))
      elif interfaces.IIdGenerator.providedBy(obj):
        attribute_set.update(('last_max_id_dict', 'last_id_dict'))
      elif classname == 'Types Tool' and klass.__module__ == 'erp5.portal_type':
        attribute_set.add('type_provider_list')

    for attribute in list(obj_dict.keys()):
      if attribute in attribute_set or attribute.startswith('_cache_cookie_') or attribute.startswith('_v'):
        del obj_dict[attribute]

    return obj_dict

InitializeClass(DiffTool)