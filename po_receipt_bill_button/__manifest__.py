{
    'name': 'PO Receipt Bill/Credit Button',
    'version': '19.0.1.0.0',
    'summary': 'Show Create Bill only for receipts and Create Credit Note for returns on PO',
    'category': 'Purchase',
    'author': 'Raqmi',
    'license': 'LGPL-3',
    'depends': ['purchase_stock', 'account'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
