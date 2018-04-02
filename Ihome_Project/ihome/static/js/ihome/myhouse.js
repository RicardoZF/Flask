// $(document).ready(function(){
//     $(".auth-warn").show();
// })

$(document).ready(function(){
    // 对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
    $.get("/api/v1_0/users/auth", function(resp){
        if (resp.errno == 4101) {
            // 用户未登录
            location.href = "/login.html";
        } else if (resp.errno == 0) {
            // 未认证的用户，在页面中展示 "去认证"的按钮
            if (!(resp.data.real_name && resp.data.id_card)) {
                $(".auth-warn").show();
                return;
            }
        }
    });
});