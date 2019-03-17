function adv() {
            var xhr = new XMLHttpRequest();
            var url = '/test';
            xhr.open('GET',url,true);
            xhr.send();
            xhr.onreadystatechange=function () {
                if(xhr.status==200&&xhr.readyState==4){
                    var res=xhr.responseText;
                    document.getElementById('guanggao').innerHTML=res;
                }
            }
        }
function adv1() {
    var xhr = new XMLHttpRequest();
    var url = '/test1';
    xhr.open('GET',url,true);
    xhr.send();
    xhr.onreadystatechange=function () {
        if(xhr.status==200&&xhr.readyState==4){
            var res=xhr.responseText;
            document.getElementById('guanggao2').innerHTML=res;
        }
    }
}
window.onload=function () {
     setInterval('adv()',5*1000);
     setInterval('adv1()',5*1000);
}