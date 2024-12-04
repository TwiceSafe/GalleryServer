import multiprocessing
import time

import requests

url = 'http://localhost:8000/api/v1/repository/gallery/commit'

num_workers = 4


def test_update():
    ret = __get_all_workers(num_workers, url)
    __print_responses(ret)

    requests.post(url, json={"haha": 123}, headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb20udHdpY2VzYWZlLmdhbGxlcnkiLCJpYXQiOjE3MzMzMTQ0MjAsImV4cCI6MTc2NDg1MDQyMCwic3ViIjoiMGZmNzUxMmItNWYxYS00NzVmLWFmNTctZmI3MDNhMzc4NjgxLmZjZTgwMjNkLTI0YjUtNDIyYy05ZWQ5LTBkMGExZjc4Y2M0NCJ9.oD91EyPi-T3AxS5-qXGrxf0s7IpGbQeXTp5idAtBfi0"})

    ret = __get_all_workers(num_workers, url)
    __print_responses(ret)


def __get_all_workers(num_workers, url, body=None):
    print('Getting data from workers...')
    responses = {}
    while len(responses) < num_workers:
        ret = requests.get(url+"/1", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb20udHdpY2VzYWZlLmdhbGxlcnkiLCJpYXQiOjE3MzMzMTQ0MjAsImV4cCI6MTc2NDg1MDQyMCwic3ViIjoiMGZmNzUxMmItNWYxYS00NzVmLWFmNTctZmI3MDNhMzc4NjgxLmZjZTgwMjNkLTI0YjUtNDIyYy05ZWQ5LTBkMGExZjc4Y2M0NCJ9.oD91EyPi-T3AxS5-qXGrxf0s7IpGbQeXTp5idAtBfi0"})
        res = ret.text.split('|')

        worker_pid = res[0].strip()
        worker_value = res[1].strip()
        if worker_pid not in responses:
            responses[worker_pid] = worker_value

    return responses


def __print_responses(responses):
    for k, v in responses.items():
        print(f'[Worker {k}] {v}')


test_update()
