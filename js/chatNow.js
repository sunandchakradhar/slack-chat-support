$.chatNow = function(opts){
    // opts.labelText
    //opts. width
    //opts.height
    var user;
    opts = $.extend({
        apiBaseUrl: '',
        label: 'Live Support!',
        width: 275,
        height: 300
    }, opts );


    var $me = $('<div class="cn-chat-now-client">\
        <a href="javascript:void(0)" class="cn-chat-label"></a>\
        <div class="cn-chat-action ">\
            <div class="chat-list">\
                <div class="cnt-chat-form">\
                    <input type="text" class="cn-chat-name cs-chat-input" placeholder="Your Name*" /><br/>\
                    <input type="text" class="cn-chat-email cs-chat-input" placeholder="Email*" /><br/>\
                    <button type="button" class="cn-chat-button" >Start Chat</button>\
                </div>\
            </div>\
            <div class="chat-box-wrap">\
                <textarea class="chat-box"></textarea>\
            </div>\
        </div>\
    </div>');
    $("body").append($me);
    var $label = $me.find(".cn-chat-label"),
    $ac = $me.find(".cn-chat-action"),
    $list = $me.find(".chat-list"),
    $box = $me.find(".chat-box"),
    last = false,
    timer;
    $label.html(opts.label);
    $ac.height(opts.height-$label.height());
    $list.height(opts.height-$label.height() - 51);

    $me.find(".cn-chat-button").click(function(){
        var name = $me.find(".cn-chat-name"),
            email= $me.find(".cn-chat-email");
        if($.trim(name.val()) == ''){
            return alert("Invalid name!");
        }
        if($.trim(email.val()) == ''){
            return alert("Invalid name!");
        }
        initChat({
            name: name.val(),
            email: email.val()
        });
    });

    $label.click(function(){
        if(!$me.data("init")){
            initChat()
        }
        // debugger;
        // alert(opts.height+'---'+$label.height());
        // $ac.height(opts.height-$label.height())
        $ac.toggle();
    });

    $box.keypress(function(e) {
        if(e.which == 13) {
            postMsg();
        }
    });

    $me.css({
        position:"fixed",
        bottom: 0,
        right: 25,
        width: opts.width,
    });

    function initChat(params){
        params = params || {};
        console.log(params);
        $.post(opts.apiBaseUrl+'/get-token', params, function(resp){
            if(resp.success){
                $me.data("init", true);
                $me.find(".cnt-chat-form").hide();
                $me.find(".chat-box").show();
                user = resp["data"]["support_user"]
                loadMessages();
            }else{
                console.log(resp);
                // alert("error");
            }
        });

    }
    function addChatMessage(msg){
        // debugger;
        // console.log('<div id="msg_'+msg.ts+'" class="chat-msg">'+msg.user+': '+msg.text+'</div>');
        if(msg.type !="message"){
            return;
        }
        if(msg.subtype && msg.subtype != "bot_message"){
            return;
        }

        var msg_id = msg.ts.replace('.', "-"),
            user = "support";
            msg_text = msg.txt;
        if(msg.bot_id && msg.subtype == "bot_message"){
            user = "me"
        }
        $msg = $('<div id="msg_'+msg_id+'" class="chat-msg"><b>'+user+'</b>: '+msg.text+'</div>');
        console.log($list.find('#msg_'+msg_id).length)
        $list.find('#msg_'+msg_id).remove();
        $list.append($msg);
        last = msg.ts;
    }

    function loadMessages(){
        var params = {}
        if(last){
            params["last"] = last;
        }
        $.get(opts.apiBaseUrl+'/get-chat',params,function(resp){
            if(resp.success){
                var messages =  resp.data.reverse();
                if(messages.length){
                    $(messages).each(function(i, msg){
                        addChatMessage(msg)
                    });
                }
            }
            timer = setTimeout(function(){
                loadMessages();
            }, 5000)
        });
    }
    function postMsg(){
        var msg = $box.val();
        if($.trim(msg) == ""){
            return;
        }
        $box.val("");
        $.post(opts.apiBaseUrl+'/send',{
            msg: msg
        }, function(resp){
            if(resp.success){
                clearTimeout(timer);
                loadMessages();
            }
        });
    }

    (function handleCrossDomain(){
        $.get(opts.apiBaseUrl+'/',function(){
            // do nothing.
        })
    })();

}
