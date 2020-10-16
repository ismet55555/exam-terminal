from fpdf import FPDF

document = FPDF()
document.set_font('Times', '', 12)
document.add_page()
TEMPLATE = '''
Report generated at {now}
Covering data from {start_time} to {end_time}


Summary
-------
TOTAL INCOME: $ {income}
TOTAL UNIT: {units} units
AVERAGE DISCOUNT: {discount}%
'''

def format_full_tmp(timestamp):
    return timestamp.datetime.isoformat()

def format_brief_tmp(timestamp):
    return timestamp.datetime.strftime('%d %b')

text = TEMPLATE.format(now=format_full_tmp(delorean.utcnow()),
                        start_time=format_brief_tmp(summary['start_time']),
                        end_time=format_brief_tmp(summary['end_time']),
                        income=summary['total_income'],
                        units=summary['units'],
                        discount=summary['average_discount'])

document.multi_cell(0, 6, text)
document.ln()
document.output(temp_file)