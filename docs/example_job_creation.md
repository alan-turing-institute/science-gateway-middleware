Example job creation:

```shell
curl -X POST \
  http://localhost:5000/api/setup/cfa6521e-a123-4a76-a04e-c367b6da169a \
  -H 'content-type: application/json' \
  -d '{
    "name": null,
    "status": "new",
    "scripts": [
        {
            "source_uri": "./resources/scripts/setup_job.sh",
            "action": "run",
            "destination_path": "./"
        }
    ],
    "id": "cfa6521e-a123-4a76-a04e-c367b6da169a",
    "case": {
        "id": "af7fd241-e816-40e5-9a70-49598a452b7b",
        "uri": null,
        "description": "Test transfer of run script",
        "label": null,
        "thumbnail": null
    },
    "uri": "https://science-gateway-middleware.azurewebsites.net/api/jobs/7b86fd40-3fcd-4367-b12b-ed834320d5c0",
    "description": null,
    "end_datetime": null,
    "start_datetime": null,
    "families": [],
    "user": null,
    "creation_datetime": "2017-08-21T09:56:01.621575+00:00",
    "templates": [],
    "inputs": []
}'
```

