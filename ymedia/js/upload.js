var uploadFileMaxSize = 524288 //512K
var uploadSFhtml='\
<form name="upfile_form" method="POST" enctype="multipart/form-data">\
  <span class="file"><input type="file" name="single_file" id="upload_file" onchange="SubmitSingleFile(this);" /></span>\
  <span id="upload_notes"></span>\
  <iframe name="upload_iframe" style="display:none;"></iframe>\
</form>\
';

function CreateUploadForm () {
    document.getElementById("upload_form").innerHTML = uploadSFhtml;
};

function SubmitSingleFile(fileObj) {


    if(fileObj.value != "") {

        var size;
        //判断文件大小
        if(window.ActiveXObject) {
            //IE浏览器
            var image = new Image();
            image.dynsrc =  filePath;
            //alert(image.fileSize);
            size = image.fileSize;
        } else if(navigator.userAgent.indexOf("Firefox")!=-1) {
            //火狐浏览器
            size = document.getElementById("upload_file").files[0].fileSize;
            //alert(size);
        };

        if (size > uploadFileMaxSize) {
            document.getElementById("upload_notes").innerHTML = '文件太大： ' + size + '(最大大小： ' + uploadFileMaxSize + ')';
            return false;
        }

        var form = document.forms['upfile_form'];
        var topicIDOBJ = document.getElementById("topicID");
        if (!topicIDOBJ) {
            topicID = 0;
        } else {
            topicID = topicIDOBJ.childNodes[0].nodeValue;
        }

        form.target = "upload_iframe";
        form.action = "/ydata/uploadsf/" + topicID + "/";
        form.submit();
    }

    return false;
};

function AfterSubmit(id, name, show_url, download_url, notes) {

    if (notes != '') {
        document.getElementById("upload_notes").innerHTML = notes + '[<a href="' + show_url + '" target="_blank">查看</a>]';
        return false;
    }

    var td1 = document.createElement("td");
    td1.innerHTML = id;

    var td2 = document.createElement("td");
    td2.innerHTML = '<span><a href="' + show_url + '">' + name + '</a> [' + '<a href="' + download_url + '">下载</a>' + ']</span>';

    var td3 = document.createElement("td");
    td3.innerHTML = '<span>无</span>';

    var tr = document.createElement("tr");
    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);

    document.getElementById("upload").appendChild(tr);
    document.getElementById("upload_form").innerHTML = '';

    return false;
};


function UploadError(notes) {
    document.getElementById("upload_notes").innerHTML = notes;
    return false;
}


function updateAttachmentInfo(id) {
    var xmlHttp;
 
    try {
        // Firefox, Opera 8.0+, Safari
        xmlHttp=new XMLHttpRequest();
    }
    catch (e) {
        // Internet Explorer
        try {
            xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch (e) {
            try {
                xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
            }
            catch (e) {
                alert("您的浏览器不支持AJAX！");
                return false;
            }
        }
    }

    xmlhttp.onreadystatechange=function() {

        if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            document.getElementById("myDiv").innerHTML=xmlhttp.responseText;
        }
    }
    xmlhttp.open("POST","/ajax/demo_post.asp",true);
    xmlhttp.send();
}
