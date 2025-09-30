"""
Permissions configuration for user roles.

This file contains the matrix of permissions for different user roles.
Changes to this file will be applied via migrations when deploying to server.
"""

ROLE_GROUPS = {
    'ORG_ADMIN': 'Администратор организации',
    'CLIENT': 'Заказчик',
    'FOREMAN': 'Прораб',
    'INSPECTOR': 'Инспектор',
}


MODEL_PERMS_MAP = {
    # model_label: {group: [codename,..]}
    'objects.constructionobject': {
        'CLIENT': ['add_constructionobject', 'change_constructionobject', 'delete_constructionobject', 'view_constructionobject', 'can_confirm_geozone'],
        'FOREMAN': ['view_constructionobject'],
        'INSPECTOR': ['view_constructionobject', 'can_confirm_geozone'],
    },
    'objects.openingchecklist': {
        'CLIENT': ['add_openingchecklist', 'change_openingchecklist', 'delete_openingchecklist', 'view_openingchecklist'],
        'FOREMAN': ['view_openingchecklist'],
        'INSPECTOR': ['view_openingchecklist'],
    },
    'schedules.workitem': {
        'CLIENT': ['add_workitem', 'change_workitem', 'delete_workitem', 'view_workitem'],
        'FOREMAN': ['view_workitem', 'can_set_actual'],
        'INSPECTOR': ['view_workitem'],
    },
    'materials.ocrresult': {
        'FOREMAN': ['can_run_ocr', 'view_ocrresult'],
        'INSPECTOR': ['can_validate_ttn', 'view_ocrresult'],
        'CLIENT': ['can_approve_ttn', 'view_ocrresult'],
    },
    'issues.remark': {
        'CLIENT': ['add_remark', 'change_remark', 'view_remark', 'can_comment_issue', 'can_close_issue'],
        'INSPECTOR': ['view_remark', 'can_comment_issue', 'can_verify_issue'],
        'FOREMAN': ['view_remark', 'can_comment_issue'],
    },
    'issues.violation': {
        'INSPECTOR': ['add_violation', 'change_violation', 'view_violation', 'can_comment_issue', 'can_close_issue'],
        'CLIENT': ['view_violation', 'can_comment_issue', 'can_verify_issue'],
        'FOREMAN': ['view_violation', 'can_comment_issue'],
    },
    'audit.auditlog': {
        'CLIENT': ['can_view_auditlog', 'view_auditlog'],
        'INSPECTOR': ['can_view_auditlog', 'view_auditlog'],
    },
}