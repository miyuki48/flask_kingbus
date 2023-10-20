$(function () {
    var dateFormat = "mm/dd/yy",
        from = $("#startDate")
            .datepicker({
                defaultDate: "+0w",
                changeMonth: true,
                numberOfMonths: 2,  //顯示兩個月可以選舉
                minDate: 0,         //最早可選取日期:今日
                maxDate: "+14D"     //最晚可選取日期:今日+14天
            })
            .on("change", function () {
                to.datepicker("option", "minDate", getDate(this));
            }),
        to = $("#finalDate").datepicker({
            defaultDate: "+0w",
            changeMonth: true,
            numberOfMonths: 2,
            minDate: 0,
            maxDate: "+14D"
        })
            .on("change", function () {
                from.datepicker("option", "maxDate", getDate(this));
            });

    function getDate(element) {
        var date;
        try {
            date = $.datepicker.parseDate(dateFormat, element.value);
        } catch (error) {
            date = null;
        }

        return date;
    }
});