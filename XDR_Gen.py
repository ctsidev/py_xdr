import json, os

class XDR_Gen:
    def __init__(self, project_id, basis):
        self.project_id = project_id
        self.basis = basis
        self.csn_tables = {
            'adt': 'event_datetime_in',
            'appt': 'appointment_datetime',
            'enc': 'encounter_date',
            'encdx': 'diagnosis_date',
            'flow': 'vital_sign_taken_time',
            'opr': 'order_time',
            'lab': 'order_time',
            'med': 'order_date',
            'note': 'create_datetime',
            'pl': 'noted_date',
            'proc': 'procedure_date'
        }

    def generate(self, sel_tables):
        base_script = '-- GENERATED BY PYXDR --\n\n'
        spool_script = 'set feedback off\nset termout off\nset markup csv on quote on\n\n'
        tables = json.load(open('tables.json'))
        sql_tables = []
        enc_tables = []
        for table in tables:
            name = table['NAME']
            if name in sel_tables:
                for sql_table in table['TABLES']:
                    if sql_table not in sql_tables:
                        sql_tables.append(sql_table)

                        if sql_table in self.csn_tables:
                            enc_tables.append(sql_table)

                elements = sel_tables[name]
                cols = ''
                for element in elements:
                    if 'date' in element.lower() or 'time' in element.lower() or element.lower() == 'dob':
                        element = f"to_char({element}, 'mm/dd/yyyy hh24:mi') {element}"
                    cols += f'\t,{element}\n'

                f = open(os.path.join('table_scripts', 'spool_tables', name), 'r').read()
                f = f.replace('<<COLS>>', cols[:-1])
                f = f.replace('<<PROJECT_ID>>', self.project_id)
                spool_script += f

        for sql_table in sql_tables:
            f = open(os.path.join('table_scripts', 'base_tables', sql_table), 'r').read()
            f = f.replace('<<PROJECT_ID>>', self.project_id)
            if self.basis == 'Patient_Based':
                f = f.replace('<<LINK_TBL>>', 'pat')
                f = f.replace('<<LINK_COL>>', 'pat_id')
                f = f.replace('<<PL_LINK_STR>>', 't.pat_id = pl.pat_id')
                f = f.replace('<<LAB_LINK_STR>>', 'JOIN i2b2.lz_clarity_enc enc ON t.pat_id = enc.pat_id\nJOIN i2b2.lz_clarity_labs lab ON enc.pat_enc_csn_id = lab.pat_enc_csn_id')
            elif self.basis == 'Encounter_Based':
                f = f.replace('<<LINK_TBL>>', 'enc')
                f = f.replace('<<LINK_COL>>', 'pat_enc_csn_id')
                f = f.replace('<<PL_LINK_STR>>', 't.pat_enc_csn_id = pl.problem_ept_csn')
                f = f.replace('<<LAB_LINK_STR>>', 'JOIN i2b2.lz_clarity_labs lab ON t.pat_enc_csn_id = lab.pat_enc_csn_id')        
            base_script += f + '\n\n'
                
        
        ipenc_lookup = ''
        date_range = ''
        for key in enc_tables:
            ipenc_lookup += f"select distinct pat_enc_csn_id from xdr_{self.project_id}_{key}\nunion\n"
            date_range += f"select min(to_date({self.csn_tables[key]})) mindate, max(to_date({self.csn_tables[key]})) maxdate\n"
            date_range += f"from xdr_{self.project_id}_{key}\nwhere {self.csn_tables[key]} <= current_date\nunion\n"

        ipenc_lookup = f"""
-- IPENC
drop table xdr_{self.project_id}_ipenc purge;
create table xdr_{self.project_id}_ipenc as
select pat_enc_csn_id
    ,'IP_' || (bip.encounter_num + (101101101 * {self.project_id})) ip_enc_id
from (
{ipenc_lookup[:-7]}
) e
join i2b2.bip_encounter_link bip on e.pat_enc_csn_id = bip.encounter_ide
;
"""
        date_range = f"""
-- DATE RANGE
select to_char(min(mindate), 'mm/dd/yyyy') mindate, to_char(max(maxdate), 'mm/dd/yyyy') maxdate
from (
{date_range[:-7]}
)
;
"""

        return { 
            f"xdr_{self.project_id}.sql": base_script + ipenc_lookup + date_range,
            f"xdr_{self.project_id}_SPOOL.sql": spool_script + 'exit'
        }