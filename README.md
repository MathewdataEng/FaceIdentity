# FaceIdentityApp
This app properly not gonna run any more because the package version confict
    <h1 > Hệ thống nhận diện khuôn mặt </h1>
        <br>
            <p>
                Hệ thống nhận dạng khuôn mặt là một ứng dụng cho phép máy tính tự động xác định 
hoặc nhận dạng một người nào đó từ một bức hình ảnh kỹ thuật số hoặc một khung 
hình từ một video.
            </p>
            <img src="/static/images/content/tongquan.svg" class="image-fluid" width="900" alt="">
            <p>
                Hình trên cho thấy, bài toán nhận diện khuôn mặt trong ảnh tự nhiên được xử lí qua 2 giai đoạn chính: 
                <br>
                <li>Phát hiện khuôn mặt</li> 
                <li>Nhận dạng khuôn mặt</li>
                <li>Nhận dạng cảm xúc</li>
                <br>
                Hai mô hình này nối tiếp với nhau, ngõ ra của 
                mô hình phát hiện khuôn mặt sẽ qua bước xử lí trung gian là cắt ảnh khuôn mặt, các 
                ảnh đã cắt sẽ là đầu vào của mô hình nhận diện. Kết quả sẽ là việc gán nhãn tên và cảm xúc của khuôn mặt.
            </p>
        <br>

        <h4>1. Huấn luyện Model nhận diện khuôn mặt </h4>
        <p>Bao gồm 4 bước:
        </p> 
        <ol>
            <li>Định vị khuôn mặt</li>
            <li>Tiền xử lí</li>
            <li>Trích xuất đặc trưng</li>
            <li>Face Recognition Model</li>
            <li>Tạo Pipeline</li>
        </ol>
        <p>Bên dưới là sơ đồ quá trình huấn luyện các bước </p>
        <img class="image-fluid" width="900" src="/static/images/content/training_flow.svg" alt="">
        <p></p>
        <h4>2. Ứng dụng Web</h4>
        <p>Phát triển dứng dụng Web dựa trên thư viện Flask
        </p> 
        <ol>
            <li>Phát triển ứng dụng Web
                <ul>
                    <li>Flask - Web Server Gateway Interphase (Backend)</li>
                    <li>HTML - Layout (Frontend)</li>
                    <li>Bootstrap - Styling (Frontend)</li>
                </ul>
            </li>
            <li>Tích hợp Machine Learning model</li>
            <li>Deploy Web App</li>
        </ol>
        <p>
            Ứng dụng Web bao gồm các trang
        </p>
        <ol>
            <li><h5><a class="nav-item nav-link" href="/">Home</a></h5></li>
            <li><h5><a class="nav-item nav-link" href="{{ url_for('index') }}">RTSP links</a></h5></li>
            <li><h5><a class="nav-item nav-link" href="{{ url_for('display') }}">App</a></h5></li>
        </ol>

        <h4>3. Triển khai</h4>
        <ol>
            <li>Kết nối Camera</li>
            <li>Deploy Web App </li>
            <li>Routing for Internet Connection </li>
        </ol> 
</div>
