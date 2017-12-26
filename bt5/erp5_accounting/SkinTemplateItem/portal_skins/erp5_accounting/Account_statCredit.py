"""Total credit of all accounting transactions having this
account as a node
"""
kw.update(
  node_uid = context.getUid(),
  omit_asset_increase = 1,
)
kw.update(
  **context.getPortalObject().portal_selections.getSelectionParamsFor(selection_name))

# here, or 0 is to prevent displaying "- 0"
return - context.Node_statAccountingBalance(**kw) or 0
