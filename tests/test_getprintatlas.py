import logging
import json

LOGGER = logging.getLogger('server')

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


def test_atlas_getprint_failed(client):
    """  Test getcapabilites response
    """
    projectfile = "atlas_simple.qgs"

    # Make a failed request no template
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: TEMPLATE is required'

    # Make a failed request no EXP_FILTER
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: EXP_FILTER is required'

    # Make a failed request with invalid EXP_FILTER (not well formed)
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == (
        'ATLAS - Error from the user while generating the PDF: Expression is invalid: \nsyntax error, unexpected $end, expecting COMMA or \')\'')

    # Make a failed request with invalid EXP_FILTER (unknown field)
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=fakeId in (1, 2)"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: Expression is invalid, eval error: Column \'fakeId\' not found'

    # Make a failed request with invalid TEMPLATE (unknown layout)
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=Fakelayout1&EXP_FILTER=id in (1, 2)"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: Layout not found'

    # Make a failed request with invalid SCALE and SCALES (can not be used together)
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2)&SCALE=5000&SCALES=10000,5000"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: SCALE and SCALES can not be used together.'

    # Make a failed request with invalid SCALE
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2)&SCALE=5000n"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: Invalid number in SCALE.'

    # Make a failed request with invalid SCALES
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2)&SCALES=10000n,5000"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: Invalid number in SCALES.'

    # Make a failed request on a project without atlas layout
    projectfile = "france_parts.qgs"
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=france_parts.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2)&SCALES=10000,5000"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 400
    assert rv.headers.get('Content-Type', '').find('application/json') == 0
    b = json.loads(rv.content.decode('utf-8'))
    assert b['status'] == 'fail'
    assert b['message'] == 'ATLAS - Error from the user while generating the PDF: Layout not found'


def test_atlas_getprint(client):
    """  Test ATLAS getprint response
    """
    projectfile = "atlas_simple.qgs"

    # Make a valid request
    qs = "?SERVICE=ATLAS&REQUEST=GetPrint&MAP=atlas_simple.qgs&TEMPLATE=layout1&EXP_FILTER=id in (1, 2)"
    rv = client.get(qs, projectfile)
    assert rv.status_code == 200

    assert rv.headers.get('Content-Type', '') == 'application/pdf'
    assert rv.headers.get('Content-Type', '').find('application/pdf') == 0