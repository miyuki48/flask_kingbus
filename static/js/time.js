
// //失敗
// let startDate = "";
// let times = new Date();
// let year = times.getFullYear();
// let month = times.getMonth() + 1;
// let date = times.getDate();
// let today = (month < 10 ? '0' + month : month) + "/" +
//     (date < 10 ? '0' + date : date) + "/" +
//     year;
// let tomorrow = (month < 10 ? '0' + month : month) + "/" +
//     (date + 1 < 10 ? '0' + (date + 1) : date + 1) + "/" +
//     year;

// function changeStartDate() {
//     startDate = document.getElementById("startDate").value;
//     console.log(startDate);
//     console.log(today);
//     if (startDate == today && times.getHours < 22) {
//         let time = new Date();
//         $('.timepicker').timepicker({
//             timeFormat: 'H:mm ',
//             interval: 10,
//             minTime: ((time.getHours()) + 2 < 10 ? '0' + time.getHours() + 2 : time.getHours()) + 2 + ':' +
//                 ((time.getMinutes()) < 10 ? '0' + time.getMinutes() : time.getMinutes()),
//             maxTime: '23:59',
//             defaultTime: '10:00',
//             startTime: '10:10',
//             dynamic: false,
//             dropdown: true,
//             scrollbar: false
//         });
//     }
//     else if (startDate == today) {
//         $('.timepicker').html("無法選擇");
//     }
//     else if (startDate == tomorrow && 22 <= times.getHours < 24) {

//         $('.timepicker').timepicker({
//             timeFormat: 'H:mm',
//             interval: 10,
//             minTime: '00:00',
//             maxTime: '23:59',
//             defaultTime: '07:00',
//             startTime: '07:10',
//             dynamic: false,
//             dropdown: true,
//             scrollbar: false
//         });
//     }
//     else {
//         $("#datepicker").datepicker({
//             dateFormat: "yy-mm-dd" //修改顯示順序
//         });

//         $('.timepicker').timepicker({
//             timeFormat: 'H:mm',
//             interval: 10,
//             minTime: '00:00',
//             maxTime: '23:59',
//             defaultTime: '07:00',
//             startTime: '07:10',
//             dynamic: false,
//             dropdown: true,
//             scrollbar: false
//         });

//     }

// }

// // console.log((times.getMonth() + 1) + "/" + times.getDay() + "/" + times.getFullYear);




//初始化jquery選擇日期套件、初始化jquery選擇時間套件
var today = new Date();
$(".datepicker").datepicker();//利用jquery套件選擇日期
// $('.datepicker').datepicker({ dateFormat: 'yy-mm-dd' });//要客製化日期格式的話，可把這行註解拿掉，並把上一行註解

//修正datepicker選擇某個日期之後，會自動跳到畫面上第一個textbox的問題
$('#txtStartDate').on('change', function () {
    setTimeout(function () {
        $('#divModal').focus();//focus到另一個按鈕element，避免被發現跳到畫面上第一個textbox XD
    }, 125);
});

//客製化日期的初始值
//開始時間與結束時間預設間隔1小時
//預設開始時間帶入下一個小時，如果會議的結束時間已經超過下班時間
//則自動帶入明天早上9:00
var defaultStartTime;
var defaultEndTime;
if (parseInt(today.getHours() + 2) >= 18) {
    defaultStartTime = '9'
    defaultEndTime = '10';
}
else {
    defaultStartTime = (today.getHours() + 1).toString()
    defaultEndTime = (today.getHours() + 2).toString()
}

//預設日期時間帶入今天    
var dateString = (today.getMonth() + 1) + '/' + today.getDate() + '/' + today.getFullYear();
$("#txtStartDate").val(dateString);
$("#txtEndDate").val(dateString);



//預設時間範圍：8:30~17:30
$('.starttimepicker').timepicker({//利用jquery套件選擇時間
    timeFormat: 'HH:mm',
    interval: 30,
    minTime: '8:30',
    maxTime: '17:30',
    defaultTime: defaultStartTime + ':00',
    startTime: '08:30',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    //zindex: 9999999,//這行平常不用，但如果你的timepicker是放在modal開窗裡面，就必須加上zindex
});


$('.endtimepicker').timepicker({//利用jquery套件選擇時間
    timeFormat: 'HH:mm',
    interval: 30,
    minTime: '8:30',
    maxTime: '17:30',
    /* defaultTime: today.getHours.toString() + ':00',*/
    defaultTime: defaultEndTime + ':00',
    startTime: '08:30',
    dynamic: false,
    dropdown: true,
    scrollbar: true,
    //zindex: 9999999,//這行平常不用，但如果你的timepicker是放在modal開窗裡面，就必須加上zindex
});


