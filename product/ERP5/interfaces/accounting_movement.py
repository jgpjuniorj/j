# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5.interfaces.asset_movement import IAssetMovement

class IAccountingMovement(IAssetMovement):
  """
  Accounting Movement private interface specification

  The notion of debit and credit is used in accounting instead of signed
  quantity. The following calculation rules apply:

    Credit/Debit

    if quantity > 0
      source_credit = quantity
      source_debit = 0
      destination_credit = 0
      destination_debit = quantity

    if quantity < 0
      source_credit = 0
      source_debit = - quantity
      destination_credit = - quantity
      destination_debit = 0

  The cancellation amount concept from IAmount interface also applies for debit
  and credit. For a cancellation amount, the calculation rule are different:

    if quantity > 0
      source_credit = 0
      source_debit = - quantity
      destination_credit = - quantity
      destination_debit = 0

    if quantity < 0
      source_credit = quantity
      source_debit = 0
      destination_credit = 0
      destination_debit = quantity

  """
  # We must a find a way to use property sheets in or as interfaces
  # property_sheets = (PropertySheet.Price, )

  # Helper methods for single currency Accounting (debit / credit)
  def getSourceDebit():
    """
    Returns the source debit in the transaction currency
    """

  def getSourceCredit():
    """
    Returns the source credit in the transaction currency
    """

  def getDestinationDebit():
    """
    Returns the destination debit in the transaction currency
    """

  def getDestinationCredit():
    """
    Returns the destination credit in the transaction currency
    """

  # Helper methods for multi currency Accounting (debit / credit)
  def getSourceAssetDebit():
    """
    Returns the source debit in the source section management currency
    based on the source_total_asset price property
    """

  def getSourceAssetCredit():
    """
    Returns the source credit in the source section management currency
    based on the source_total_asset price property
    """

  def getDestinationAssetDebit():
    """
    Returns the destination debit in the destination section management currency
    based on the destination_total_asset price property
    """

  def getDestinationAssetCredit():
    """
    Returns the destination credit in the destination section management currency
    based on the destination_total_asset price property
    """

  # The following is really unclear -
  #   It uses getSourceInventoriatedTotalAssetPrice instead of
  #   of getSourceInventoriatedTotalAssetPrice instead of getSourceTotalAssetPrice
  #   I can only see one purpose: presentation of reports in predictive accounting
  #   ie. in transactions generated by simulation which do not yet have
  #   well defined source_total_asset/destination_total_asset
  def getSourceInventoriatedTotalAssetDebit():
    """
    Unclear - XXX
    """

  def getSourceInventoriatedTotalAssetCredit():
    """
    Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetDebit():
    """
    Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetCredit():
    """
    Unclear - XXX
    """