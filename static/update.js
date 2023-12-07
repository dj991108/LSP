$(document).ready(function(){
    // 주기적으로 자세 이미지와 환경 데이터 업데이트
    setInterval(function(){
        updatePosture();
        updateEnvironment();
    }, 500); // 0.5초마다 업데이트
});

function updatePosture() {
    // AJAX 요청으로 자세 데이터 가져오기
    $.get('/posture', function(data) {
        var timestamp = new Date().getTime(); // 타임스탬프 생성
        var imageUrl = 'static/image/' + data.image + '?t=' + timestamp; // 타임스탬프를 URL에 추가
        $('#posture-image').attr('src', imageUrl); // 이미지 소스 업데이트
        $('#posture-status').text(data.status); // 자세 상태 텍스트 업데이트
    });
}

function updateEnvironment() {
    // AJAX 요청으로 환경 데이터 가져오기
    $.get('/environment', function(data) {
        $('#temperature').text('온도: ' + Math.floor(data.temp) + '°C'); // 온도 표시
        $('#temperature-advice').text(data.temp_advice); // 온도 조언 표시
        $('#humidity').text('습도: ' + Math.floor(data.hum) + '%'); // 습도 표시
        $('#humidity-advice').text(data.hum_advice); // 습도 조언 표시
        $('#light').text('조도: ' + Math.floor(data.lumi) + 'Lux'); // 조도 표시
        $('#light-advice').text(data.lumi_advice); // 조도 조언 표시
    });
}