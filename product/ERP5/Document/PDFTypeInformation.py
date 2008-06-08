##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type import USE_BASE_TYPE

if not USE_BASE_TYPE:
  from Products.ERP5Type.XMLObject import XMLObject
  
  class PDFTypeInformation(XMLObject):
    """
      Dummy class
    """
    # CMF Type Definition
    meta_type = 'ERP5 PDF Type Information'
    portal_type = 'PDF Type'
    isPortalContent = 1
    isRADContent = 1

else:
  from Products.ERP5Type.ERP5Type import ERP5TypeInformation

  class PDFTypeInformation(ERP5TypeInformation):
      """
        EXPERIMENTAL - DO NOT USE THIS CLASS BESIDES R&D
  
        A Type Information class which (will) implement
        all PDF Editor related methods in a more generic
        way.
      """
      # CMF Type Definition
      meta_type = 'ERP5 PDF Type Information'
      portal_type = 'PDF Type'
      isPortalContent = 1
      isRADContent = 1
  
      # Declarative security
      security = ClassSecurityInfo()
      security.declareObjectProtected(Permissions.AccessContentsInformation)
  
      # Default Properties
      property_sheets = ( PropertySheet.Base
                        , PropertySheet.XMLObject
                        , PropertySheet.CategoryCore
                        , PropertySheet.SimpleItem
                        , PropertySheet.Folder
                        , PropertySheet.BaseType
                      )
