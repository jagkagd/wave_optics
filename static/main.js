function showElem(){
    $.ajax({
        type: "POST",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/show",
        data: JSON.stringify(elemListElement),
        success: function(){
            updateThree();
        },
        dataType: "html"
    });
}

function updateElemList(elementList, domElemList){
    domElemList.children('li').remove();
    for(var i=0; i<elementList.length; i++){
        data = elementList[i];
        if($.isEmptyObject(data) || $.type(data[0]) === "array"){
            domElemList.append("<li class='elemListElem'>组<ul class='groupListElem'></ul></li>");
            subDomElemList = domElemList.find('ul').last();
            updateElemList(data, subDomElemList);
        }else if($.inArray(data[0], Object.keys(classInheritDict['FreeSpace']['subclasses'])) > -1){
            domElemList.append("<li class='elemListElem'>" + data[1]['z'] + "mm" + "</li>");
        }else{
            domElemList.append("<li class='elemListElem'>" + rDict[data[0]] + "</li>");
        }
    }
}

$(document).ready(function(){
    var cnt = 0;
    $('.addButton').hide();
    $('.listButton').hide();
    $('#groupList').hide();
    $("#nav ul li ul").hide();
    $('#elemList').sortable();

    var span = parseInt(prompt('尺寸(中心到边缘)(mm):', '5'));
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
            $tr.append($('<td>')).append('<input type="text" name=' + key + ' value=' +  JSON.stringify(classInheritDict[chooseBaseId]['subclasses'][chooseId][key]) + '>');
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
        cnt++;
        if($('#setPara').attr('name') === 'groupBegin'){
            groupFlag = 1;
        }else if($('#setPara').attr('name') === 'groupEnd'){
            groupFlag = 3;
        }
        var data = [$(this).siblings("table").attr('name'), {}];
        var $table = $('#setPara');
        $table.find('input').each(function(){
            data[1][$(this).attr('name')] = $(this).val();
        });
        if(groupFlag === 0){
            elemListElement.push(data);
        }else if(groupFlag === 1){
            elemListElement.push(new Array());
        }else if(groupFlag === 2){
            elemListElement[elemListElement.length - 1].push(data);
        }else if(groupFlag === 3){
            groupFlag === 0;
        }
        if(groupFlag === 1){
            groupFlag = 2;
        }else if(groupFlag === 3){
            groupFlag = 0;
        }
        updateElemList(elemListElement, $('#elemList'));
        showElem();
    });

    $('.elemListElem').live('click', function(){
        $('#setPara').empty();
        $('.addButton').hide();
        $('.listButton').show();
        var $table = $('#setPara')
        var tempElem;
        if($(this).parent().attr('class') === 'groupListElem'){
            var idx1 = $(this).index();
            var idx0 = $(this).parent().parent().index();
            tempElem = elemListElement[idx1][idx2];
            $('#change').attr('name', JSON.stringify([idx0, idx1]));
        }else{
            var idx = $(this).index();
            tempElem = elemListElement[idx];
            $('#change').attr('name', JSON.stringify([idx]));
        }
        $table.attr('name', tempElem[0]);
        var i = 0;
        for(var key in tempElem[1]){
            if(i % 2 === 0){
                $table.append($('<tr>'));
            }
            i += 1;
            var $tr = $table.children().first();
            $tr.append($('<td>')).append('<label>' + rDict[key] + ':</label>');
            $tr.append($('<td>')).append('<input type="text" name=' + key + ' value=' +  JSON.stringify(tempElem[1][key]) + '>');
        }
        return false;
    });

    $('#change').click(function(){
        var $table = $('#setPara');
        var idx = JSON.parse($('#change').attr('name'));
        var data = [$(this).siblings("table").attr('name'), {}];
        $table.find('input').each(function(){
            data[1][$(this).attr('name')] = $(this).val();
        });
        if(idx.length === 1){
            elemListElement[idx[0]] = data;
        }else if(idx.length === 2){
            elemListElement[idx[0]][idx[1]] = data;
        }
        updateElemList(elemListElement, $('#elemList'));
        showElem();
    });

    $('#del').live('click', function(){
        var idx = JSON.parse($('#change').attr('name'));
        if(idx.length === 1){
            elemListElement.splice(idx[0], 1);
        }else if(idx.length === 2){
            elemListElement[idx[0]].splice(idx[1], 1);
            if(elemListElement[idx[0]].length === 0){
                elemListElement.splice(idx[0], 1);
            }
        }
        updateElemList(elemListElement, $('#elemList'));
        showElem();
    });
    
    $('#calc').click(function(){
        $.ajax({
            type: "POST",
            async:true,
            contentType: "application/json; charset=utf-8",
            url: "/calc",
            data: JSON.stringify(elemListElement),
            success: function(data){
                console.log(data);
                updateThree();
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
            var temp = elemListElement.splice(startIdx, 1)[0];
            elemListElement.splice(endIdx, 0, temp);
            showElem();
        }
    });
});
