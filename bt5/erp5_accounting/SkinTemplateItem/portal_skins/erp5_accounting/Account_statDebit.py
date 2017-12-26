"""Total debit of all accounting transactions having this
account as a node
"""

kw.update(
  node_uid=context.getUid(),
  omit_asset_decrease=1
)
# force second update to overwrite anything by selection params
kw.update(
  **context.getPortalObject().portal_selections.getSelectionParamsFor(selection_name, REQUEST=kw.get('REQUEST', None)))

return context.Node_statAccountingBalance(**kw)
