class VifibSystemPreference:
  """Vifib System Preferences"""
  _properties = (
    { 'id'              : 'preferred_instance_cleanup_resource',
      'description'     : 'Resource used to represent fact of cleaning up Software Instance',
      'type'            : 'string',
      'default'         :  '',
      'preference'      : 1,
      'write_permission': 'Manage properties',
      'mode'            : 'w'},
    { 'id'              : 'preferred_instance_hosting_resource',
      'description'     : 'Resource used to represent fact of hosting operations on Software Instance',
      'type'            : 'string',
      'default'         :  '',
      'preference'      : 1,
      'write_permission': 'Manage properties',
      'mode'            : 'w'},
    { 'id'              : 'preferred_instance_setup_resource',
      'description'     : 'Resource used to represent fact of Software Instance setup',
      'type'            : 'string',
      'default'         :  '',
      'preference'      : 1,
      'write_permission': 'Manage properties',
      'mode'            : 'w'},
    { 'id'              : 'preferred_software_setup_resource',
      'description'     : 'Resource used to represent fact of Software Release setup',
      'type'            : 'string',
      'default'         :  '',
      'preference'      : 1,
      'write_permission': 'Manage properties',
      'mode'            : 'w'},
  )
