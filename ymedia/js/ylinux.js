function load_syntaxhighlighter () {
    SyntaxHighlighter.autoloader(
        'cpp  /ymedia/js/syntaxhighlighter/scripts/shBrushCpp.js',
        'applescript            /js/shBrushAppleScript.js'
    );

    SyntaxHighlighter.config.tagName = 'code';
    SyntaxHighlighter.defaults['toolbar'] = false;
    /*SyntaxHighlighter.defaults['gutter'] = false;*/
    SyntaxHighlighter.defaults['title'] = '<a href="http://www.ylinux.org" title="访问 YLinux.org" target="_blank">YLinux</a> 代码分享';

    function path()
    {
        var args = arguments,
        result = []
        ;
        
        for(var i = 0; i < args.length; i++)
            result.push(args[i].replace('@', '/ymedia/js/syntaxhighlighter/scripts/'));
        
        return result
    };
    
    SyntaxHighlighter.autoloader.apply(null, path(
        'applescript            @shBrushAppleScript.js',
        'actionscript3 as3      @shBrushAS3.js',
        'bash shell             @shBrushBash.js',
        'coldfusion cf          @shBrushColdFusion.js',
        'cpp c                  @shBrushCpp.js',
        'c# c-sharp csharp      @shBrushCSharp.js',
        'css                    @shBrushCss.js',
        'delphi pascal          @shBrushDelphi.js',
        'diff patch pas         @shBrushDiff.js',
        'erl erlang             @shBrushErlang.js',
        'groovy                 @shBrushGroovy.js',
        'java                   @shBrushJava.js',
        'jfx javafx             @shBrushJavaFX.js',
        'js jscript javascript  @shBrushJScript.js',
        'perl pl                @shBrushPerl.js',
        'php                    @shBrushPhp.js',
        'text plain             @shBrushPlain.js',
        'py python              @shBrushPython.js',
        'ruby rails ror rb      @shBrushRuby.js',
        'sass scss              @shBrushSass.js',
        'scala                  @shBrushScala.js',
        'sql                    @shBrushSql.js',
        'vb vbnet               @shBrushVb.js',
        'xml xhtml xslt html    @shBrushXml.js'
    ));

    SyntaxHighlighter.all();

}


function ajax_list_catalog (url) {
    $("#wiki-container-main").load(url, function () {
        $(this).addClass("list-catalog-done");
    });
}

function ajax_login () {
    // 下面两个方法都可以获取 input 的 value 
    var username = $("#username").attr("value");
    var password = $("#password")[0].value;

    $.ajax({
        url: "/account/login/ajax/",
        type: "POST",
        data: {username: username, password: password},
        success: function(msg){
            $("#account").html(msg);
        }
    });
    //alert ("username: " + username +"\npassword: " + password);
}


function ajax_logout () {
    $("#account").load("/account/logout/ajax/");
}


function ajax_create_login () {
    var loginHtml = '';
    loginHtml +='<span class="login-text">用户</span><input id="username" type="text" maxlength="30"/>'
    loginHtml += '<span class="login-text">密码</span><input id="password" type="password"/>'
    loginHtml += '<button type="button" onclick="javascript:ajax_login()">登录</button>'
    $("#account").html(loginHtml);
}