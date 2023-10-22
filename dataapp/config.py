# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

class BaseConfig(object):

    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = 'ServicePrincipal'

    # Workspace Id in which the report is present
    WORKSPACE_ID = '61fc7405-5ee8-4ba2-9b05-ec64e85c8853'
    
    # Report Id for which Embed token needs to be generated
    REPORT_ID = '8d520473-416b-4f93-80d0-323ecf97b72e'
    
    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = 'a60e2d77-3925-4eca-ace0-eecc604d922c'
    
    # Client Id (Application Id) of the AAD app
    CLIENT_ID = 'f85ee12f-73a9-43d4-8453-2db3de7848fd'
    
    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = 'nJ~8Q~7ekBIZ0TvohgIl_89adS60FxlOKCDSjcqC'
    
    # Scope Base of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE_BASE = ['https://analysis.windows.net/powerbi/api/.default']
    
    # URL used for initiating authorization request
    AUTHORITY_URL = 'https://login.microsoftonline.com/organizations'
    
    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = 'HaoXu@aita0.onmicrosoft.com'
    
    # Master user email password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = 'Xh!0135259098'