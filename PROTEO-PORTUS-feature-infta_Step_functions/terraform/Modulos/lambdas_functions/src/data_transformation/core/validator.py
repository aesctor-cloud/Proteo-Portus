def is_valid_record(record: dict) -> bool:
    required_fields = ['start_date', 'completion_date', 'value_contract', 'name_project']
    return all(record.get(field) not in [None, '', []] for field in required_fields)