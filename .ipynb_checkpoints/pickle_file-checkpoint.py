import pickle

pw = '6868'

# 파일로 저장
with open('pw.pkl', 'wb') as f:
    pickle.dump(pw, f)
    
# 파일 불러오기
with open('pw.pkl', 'rb') as f:
    data = pickle.load(f)


host_url = 'ec2-34-235-154-153.compute-1.amazonaws.com'
# 파일로 저장
with open('host.pkl', 'wb') as f:
    pickle.dump(host_url, f)
    
# 파일 불러오기
with open('host.pkl', 'rb') as f:
    host = pickle.load(f)

print(data)
print(host)