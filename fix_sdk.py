import re

def process_file():
    with open('api/session_intelligence_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Just fix _eval_device_checkpoint in the file
    content = re.sub(
        r'sdk_res = sdk_engine.register_device\(device_id, \{"ip": ip\}\)',
        r'sdk_res = sdk_engine.register_device({"device_id": device_id, "ip": ip, **data})',
        content
    )

    with open('api/session_intelligence_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed sdk_engine.register_device call")

if __name__ == "__main__":
    process_file()
