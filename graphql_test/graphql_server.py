#!/bin/python3
from flask import Flask, request, jsonify
from graphene import Schema
from schema import schema  # 导入上面定义的 schema

# apt install python3-graphene python3-flask
# test
'''
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ hello(name: \"Python\") }"}'
'''

app = Flask(__name__)

@app.route('/graphql', methods=['POST'])
def graphql():
    # 从请求体中获取 GraphQL 查询
    data = request.get_json()
    query = data.get('query')
    variables = data.get('variables')
    
    # 执行查询
    result = schema.execute(query, variables=variables)
    
    # 返回结果
    return jsonify(result.data if not result.errors else {"errors": [str(e) for e in result.errors]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)