$(document).ready(function(){
    $('.addButton').hide();
    $('.listButton').hide();
    $('#groupList').hide();
    $("#nav ul li ul").hide();
    var span = parseInt(prompt('元件尺寸(mm)：', '5'));
    var reso = parseInt(prompt('分辨率:', '2048'));
    data = {'span': span, 'reso': reso};
    $.ajax({
        type: "POST",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/set_default",
        data: JSON.stringify(data),
        success: console.log('success'),
        dataType: "html"
    });
    $("#nav ul li").click(function(e) {
      $(this).children("ul").slideToggle();
      e.stopPropagation();
    });
    $('.chooseChildItem').click(function(){
        $('.listButton').hide();
        var chooseId = $(this).attr('id');
        var chooseBaseId = $(this).parent().parent().attr('id');
        $('#setPara').attr('name', chooseId);
        var $table = $('#setPara');
        $table.empty();
        var i = 0;
        for(var key in classInheritDict[chooseBaseId]['subclasses'][chooseId]){
            if(i % 2 === 0){
                $table.append($('<tr>'));
            }
            var $tr = $table.children().first();
            $tr.append($('<td>')).append('<label>' + rDict[key] + ':</label>');
            $tr.append($('<td>')).append('<input type = "text" name = ' + key + ' value = ' +  JSON.stringify(classInheritDict[chooseBaseId]['subclasses'][chooseId][key]) + '>');
            i += 1;
        }
        $('#add').show();
        return false;
    });
    $('#groupBegin').click(function(){
        $('.listButton').hide();
        $('#setPara').attr('name', 'groupBegin');
        var $table = $('#setPara');
        $table.empty();
        $table.append('添加一个组');
        $('#add').show();
    });
    $('#groupEnd').click(function(){
        $('.listButton').hide();
        $('#setPara').attr('name', 'groupEnd');
        var $table = $('#setPara');
        $table.empty();
        $table.append('完成组的添加');
        $('#add').show();
    });
    $('#add').click(function(){
        if($('#setPara').attr('name') === 'groupBegin'){
            groupFlag = 1;
        }else if($('#setPara').attr('name') === 'groupEnd'){
            groupFlag = 3;
        }
        var data = {'type': $(this).siblings("table").attr('name'), 'group': groupFlag};
        var $table = $('#setPara');
        $table.find('input').each(function(){
            data[$(this).attr('name')] = $(this).val();
        });
        $.ajax({
            type: "POST",
            async:true,
            contentType: "application/json; charset=utf-8",
            url: "/add",
            data: JSON.stringify(data),
            success: function (data) {
                data = JSON.parse(data);
                if(data[0] === 'error'){
                    alert(data[1]);
                }else if(groupFlag === 0){
                    $('#elemList').append("<li class = 'elemListElem'>" + rDict[data[0]] + "</li>");
                    elemListElement.push(data);
                }else if(groupFlag === 1){
                    $('#elemList').append("<li class = 'elemListElem'>组<ul class = 'groupListElem'></ul></li>");
                    elemListElement.push(new Array());
                }else if(groupFlag === 2){
                    $('#elemList').find('ul').last().append("<li class = 'elemListElem'>" + rDict[data[0]] + "</li>");
                    elemListElement[elemListElement.length - 1].push(data);
                }else if(groupFlag === 3){
                    groupFlag === 0;
                }
                updateThree();
                if(groupFlag === 1){
                    groupFlag = 2;
                }else if(groupFlag === 3){
                    groupFlag = 0;
                }
                console.log(elemListElement)
            },
            dataType: "html"
        });
    });
    $('.elemListElem').live('click', function(){
        $('#setPara').empty();
        $('.addButton').hide();
        $('.listButton').show();
        var $table = $('#setPara')
        var tempElem;
        if($(this).parent().attr('class') === 'groupListElem'){
            var idx2 = $(this).index();
            var idx1 = $(this).parent().parent().index();
            tempElem = elemListElement[idx1][idx2];
            $('#change').attr('name', JSON.stringify([idx1, idx2]));
        }else{
            var idx = $(this).index();
            tempElem = elemListElement[idx];
            $('#change').attr('name', JSON.stringify([idx]));
        }
        $table.attr('name', tempElem[0]);
        console.log(tempElem);
        var i = 0;
        for(var key in tempElem[1]){
            if(i % 2 === 0){
                $table.append($('<tr>'));
            }
            i += 1;
            var $tr = $table.children().first();
            $tr.append($('<td>')).append('<label>' + rDict[key] + ':</label>');
            $tr.append($('<td>')).append('<input type = "text" name = ' + key + ' value = ' +  JSON.stringify(tempElem[1][key]) + '>');
        }
        return false;
    });
    $('#change').click(function(){
        var data = {'type': $(this).siblings("table").attr('name')};
        var $table = $('#setPara');
        var idx = JSON.parse($('#change').attr('name'));
        data['idx'] = idx;
        $table.find('input').each(function(){
            data[$(this).attr('name')] = $(this).val();
        });
        $.ajax({
            type: "POST",
            async:true,
            contentType: "application/json; charset=utf-8",
            url: "/change",
            data: JSON.stringify(data),
            success: function (data) {
                data = JSON.parse(data);
                if(groupFlag === 0){
                    elemListElement[idx[0]] = data;
                }else{
                    elemListElement[idx[0]][idx[1]] = data;
                }
                updateThree();
            },
            dataType: "html"
        });
    });
    $('#del').live('click', function(){
        var idx = JSON.parse($('#change').attr('name'));
        if(idx.length === 1){
            elemListElement.splice(idx[0], 1);
            $('#elemList li:eq(' + idx[0] + ')').remove();
        }else if(idx.length === 2){
            elemListElement[idx[0]].splice(idx[1], 1);
            $('#elemList li:eq(' + idx[0] + ') ul li:eq(' + idx[1] + ')').remove();
            if(elemListElement[idx[0]].length === 0){
                elemListElement.splice(idx[0], 1);
                $('#elemList li:eq(' + idx[0] + ')').remove();
            }
        }
        $.ajax({
            type: "POST",
            async:true,
            contentType: "application/json; charset=utf-8",
            url: "/del",
            data: JSON.stringify(idx),
            success: function(data){
                updateThree();
            },
            dataType: "html"
        });
    });
});
