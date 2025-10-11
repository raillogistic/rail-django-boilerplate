import json
from pathlib import Path
import requests


def main():
    project_dir = Path(__file__).resolve().parent
    jwt_path = project_dir / "jwt.json"
    if not jwt_path.exists():
        raise FileNotFoundError(f"jwt.json not found at {jwt_path}")

    token = json.loads(jwt_path.read_text(encoding="utf-8"))['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    query = (
        "query($app_name:String!, $model_name:String!){\n"
        "  model_metadata(app_name:$app_name, model_name:$model_name){\n"
        "    model_name app_name table_name primary_key_field\n"
        "    relationships {\n"
        "      name relationship_type related_app related_name\n"
        "      related_model {\n"
        "        model_name app_name table_name primary_key_field\n"
        "        fields { name field_type is_required }\n"
        "        relationships { name relationship_type }\n"
        "        permissions ordering abstract proxy managed\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )

    variables = {"app_name": "blog", "model_name": "Post"}
    payload = {"query": query, "variables": variables}
    url = "http://127.0.0.1:8000/graphql/"
    resp = requests.post(url, headers=headers, json=payload)
    print("Status:", resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()