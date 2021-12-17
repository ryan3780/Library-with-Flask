### URL : http://ec2-3-36-55-158.ap-northeast-2.compute.amazonaws.com

## 폴더 및 파일 구조

```
Library-with-Flask/     # root
┣ static/               # css, img, js 등 static 보관
┣ templates/            # jinja2 코드가 있는 html 파일들 폴더
┣ app.py                # 로그인/로그아웃, 회원가입, 책 대여/반납, 책 평점 부여/댓글 남기기 
┣ form.py               # 회원가입 validation
┣ models.py             # DB 생성
┗ requirements.txt      # pip list
```
## 스택
### AWS EC2 + Nginx + Gunicorn + Flask + MySQL  
## 구현 기능
- 로그인/로그아웃, 회원가입
- 책 대여/반납
- 책 평점 부여/댓글 남기기
