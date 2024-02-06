import pickle

pw = '6868'

# 파일로 저장
with open('pw.pkl', 'wb') as f:
    pickle.dump(pw, f)
    
# 파일 불러오기
with open('pw.pkl', 'rb') as f:
    data = pickle.load(f)


host = 'ec2-3-80-227-67.compute-1.amazonaws.com'
# 파일로 저장
with open('host.pkl', 'wb') as f:
    pickle.dump(host, f)
    
# 파일 불러오기
with open('host.pkl', 'rb') as f:
        host = pickle.load(f)

print(data)
print(host)