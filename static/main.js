var elemListForShow = new Array();

function getInputValue($item){
    if($item.is('input')){
        var inputType = $item.attr('type');
        if(inputType === 'text'){
            return $item.val();
        }else if(inputType === 'checkbox'){
            return ($item.attr('checked') === 'checked')? 'true': 'false';
        }
    }else if($item.is('select')){
        return $item.val();
    }
}

function showElem(){
    $('#status').text('Processing...');
    $('#status').removeClass('calc-success');
    $('#status').addClass('calc-processing');
    console.log(elemListForShow);
    $.ajax({
        type: "POST",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/show",
        data: JSON.stringify(elemListForShow),
        success: function(data){
            showFeedback(data);
            updateThree(elemListForShow);
        },
        dataType: "html"
    });
}

function updateDomElemList(elementList, domElemList){
    domElemList.children('li').remove();
    for(var i=0; i<elementList.length; i++){
        data = elementList[i];
        if($.isEmptyObject(data) || $.type(data[0]) === "array"){
            domElemList.append("<li class='elemListElem'><ul class='groupListElem'></ul></li>");
            subDomElemList = domElemList.find('ul').last();
            updateDomElemList(data, subDomElemList);
        }else if($.inArray(data[0], Object.keys(classInheritDict['FreeSpace']['subClasses'])) > -1){
            domElemList.append("<li class='elemListElem'>" + data[1]['z']['default'] + "mm" + "</li>");
        }else{
            domElemList.append("<li class='elemListElem'>" + rDict[data[0]] + "</li>");
        }
    }
}

function showElementParaPan(elem, $table){
    $table.empty();
    var i = 0;
    for(var key in elem){
        $table.append('<div class="pure-u-1-3 pure-u-md-1-3">');
        $tr = $table.children().last();
        showElementPara(elem, key, $tr);
    }
}

function showElementPara(elem, key, $tr){
    $tr.append('<label class="element-lable" for="' + key + '">' + rDict[key] + ':</label>');
    var keyType = elem[key]['annotation'];
    var inputType, enumList;
    if($.inArray(keyType, ['float', 'int', 'str']) > -1){
        inputType = "text";
    }else if(keyType === 'bool'){
        inputType = "checkbox";
    }else if($.type(keyType) === 'array'){
        if($.inArray(keyType[0], ['float', 'int']) > -1){
            inputType = "text";
        }
    }else if(keyType[0] === '|'){
        inputType = "select";
        enumList = keyType.split('|').slice(1);
    }
    if($.inArray(inputType, ["text", "str"]) > -1){
        $tr.append('<input type=' + inputType + ' name=' + key + ' value=' +  JSON.stringify(elem[key]['default']) + '>');
    }else if(inputType === 'checkbox'){
        if(elem[key]['default'] === 'true'){
            $tr.append('<input class="styled-checkbox" type=' + inputType + ' name=' + key + ' value=' + key + ' checked="checked"/>');
        }else{
            $tr.append('<input type=' + inputType + ' name=' + key + ' value=' + key + '/>');
        }
        $tr.addClass('styled-checkbox-parent');
    }else if(inputType === "select"){
        $tr.append('<select name=' + key + '>');
        $sel = $tr.find("select");
        for(var i = 0; i < enumList.length; i++){
            if(elem[key]['default'] === enumList[i]){
                $sel.append('<option value=' + enumList[i] + ' selected="selected">' + rDict[enumList[i]] + '</option>');
            }else{
                $sel.append('<option value=' + enumList[i] + '>' + rDict[enumList[i]] + '</option>');
            }
        }
    }
    $tr.find('input, select').addClass('pure-u-23-24').attr('id', key);
}

function showFeedback(data){
    data = JSON.parse(data);
    if(data === 'success'){
        $('#status').text('Done');
        $('#status').removeClass('calc-processing');
        $('#status').addClass('calc-success');
    }else{
        alert(data);
        $('#status').text('Fail');
        $('#status').removeClass('calc-processing');
        $('#status').addClass('calc-failed');
    }
}

function setDefault(data){
    $('#status').text('Processing...');
    $('#status').addClass('calc-processing');
    $('#status').removeClass('calc-success');
    $('#status').removeClass('calc-failed');
    $.ajax({
        type: "POST",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/set_default",
        data: JSON.stringify(data),
        success: function(data){
            showFeedback(data);
        },
        dataType: "html"
    });
}

$(document).ready(function(){
    var cnt = 0;
    $('#add').hide();
    $('.list-button').hide();
    $('#groupList').hide();
    $("#nav ul li ul").hide();
    $('#elemList').sortable();

    var span = parseInt(prompt('尺寸(中心到边缘)(mm):', '5'));
    var reso = parseInt(prompt('分辨率:', '2048'));

    data = {'span': span, 'reso': reso};
    setDefault(data);
    
    $("#nav ul li").click(function(e){
      $(this).children("ul").slideToggle();
      e.stopPropagation();
    });

    $('.chooseChildItem').click(function(){
        $('.list-button').hide();
        var chooseId = $(this).attr('id');
        $('#setPara').attr('name', chooseId);
        var $table = $('#setPara');
        $table.empty();
        var elem = {};
        $.extend(true, elem, subClassesInfo[chooseId]['args']);
        showElementParaPan(elem, $table);
        $('#add').show();
        return false;
    });

    $('#groupBegin').click(function(){
        $('.list-button').hide();
        $('#setPara').attr('name', 'groupBegin');
        var $table = $('#setPara');
        $table.empty();
        $table.append('添加一个组');
        $('#add').show();
    });

    $('#groupEnd').click(function(){
        $('.list-button').hide();
        $('#setPara').attr('name', 'groupEnd');
        var $table = $('#setPara');
        $table.empty();
        $table.append('完成组的添加');
        $('#add').show();
    });

    $('#add').click(function(){
        cnt++;
        if($('#setPara').attr('name') === 'groupBegin'){
            groupFlag = 1;
        }else if($('#setPara').attr('name') === 'groupEnd'){
            groupFlag = 3;
        }else{
            var className = $('#setPara').attr('name');
            var args = {};
            $.extend(true, args, subClassesInfo[className]['args']);
            var data = [className, args];
            var $table = $('#setPara');
            $table.find('input, select').each(function(){
                data[1][$(this).attr('name')]['default'] = getInputValue($(this));
            });
        }
        if(groupFlag === 0){
            elemListForShow.push(data);
        }else if(groupFlag === 1){
            elemListForShow.push(new Array());
        }else if(groupFlag === 2){
            elemListForShow[elemListForShow.length - 1].push(data);
        }else if(groupFlag === 3){
            groupFlag === 0;
        }
        if(groupFlag === 1){
            groupFlag = 2;
        }else if(groupFlag === 3){
            groupFlag = 0;
        }
        updateDomElemList(elemListForShow, $('#elemList'));
        showElem();
    });

    $('.elemListElem').live('click', function(){
        $('#setPara').empty();
        $('#add').hide();
        $('.list-button').show();
        var $table = $('#setPara')
        var tempElem;
        if($(this).parent().attr('class') === 'groupListElem'){
            var idx1 = $(this).index();
            var idx0 = $(this).parent().parent().index();
            tempElem = elemListForShow[idx0][idx1];
            $('#change').attr('name', JSON.stringify([idx0, idx1]));
        }else{
            var idx = $(this).index();
            tempElem = elemListForShow[idx];
            $('#change').attr('name', JSON.stringify([idx]));
        }
        $table.attr('name', tempElem[0]);
        showElementParaPan(tempElem[1], $table);
        return false;
    });

    $('#change').click(function(){
        var $table = $('#setPara');
        var idx = JSON.parse($('#change').attr('name'));
        var className = $('#setPara').attr('name');
        var args = {};
        $.extend(true, args, subClassesInfo[className]['args']);
        var data = [className, args];
        $table.find('input, select').each(function(){
            data[1][$(this).attr('name')]['default'] = getInputValue($(this));
        });
        if(idx.length === 1){
            elemListForShow[idx[0]] = data;
        }else if(idx.length === 2){
            elemListForShow[idx[0]][idx[1]] = data;
        }
        updateDomElemList(elemListForShow, $('#elemList'));
        showElem();
    });

    $('#del').live('click', function(){
        var idx = JSON.parse($('#change').attr('name'));
        if(idx.length === 1){
            elemListForShow.splice(idx[0], 1);
        }else if(idx.length === 2){
            elemListForShow[idx[0]].splice(idx[1], 1);
            if(elemListForShow[idx[0]].length === 0){
                elemListForShow.splice(idx[0], 1);
            }
        }
        updateDomElemList(elemListForShow, $('#elemList'));
        showElem();
    });
    
    $('#calc').click(function(){
        $('#status').text('Processing...');
        $('#calc').addClass('pure-button-disabled');
        $.ajax({
            type: "POST",
            async:true,
            contentType: "application/json; charset=utf-8",
            url: "/calc",
            data: JSON.stringify(elemListForShow),
            success: function(data){
                showFeedback(data);
                updateThree();
                $('#calc').removeClass('pure-button-disabled');
            },
            dataType: "html"
        });
    });

    $('#elemList').sortable({
        start: function(event, ui){
            var startIdx = ui.item.index();
            ui.item.data('startIdx', startIdx);
        },
        update: function(event, ui){
            var startIdx = ui.item.data('startIdx');
            var endIdx = ui.item.index();
            var temp = elemListForShow.splice(startIdx, 1)[0];
            elemListForShow.splice(endIdx, 0, temp);
            showElem();
        }
    });
});
