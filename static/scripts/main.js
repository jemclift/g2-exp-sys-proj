function fillBase64(element) {

    const reader = new FileReader();
    reader.readAsDataURL(element.files[0]);

    reader.addEventListener("load", function () {

        document.getElementById("img-base64-txt").value = reader.result

    }, false);

}

function timeSince(date) {
    // time delta in seconds
    let seconds = Math.floor((new Date() - date) / 1000);

    let index = 0
    const units = ['year', 'month', 'day', 'hour', 'minute', 'second']
    const divisors = [31536000, 2592000, 86400, 3600, 60, 1]

    let interval = seconds / divisors[index]

    while (interval <= 1) {
        index ++ 
        interval = seconds / divisors[index]
    }

    // round down to integer value
    let value = Math.floor(interval)
    let unit = units[index]

    // plural units
    if ( value > 1 ) { unit += 's' }

    return value + ' ' + unit

}

function formatAllDates() {
    let all_date_elements = document.getElementsByClassName("post-date")

    for (element of all_date_elements) {
        let date_string = element.innerHTML
        let post_date = Date.parse(date_string)
        element.innerHTML = "posted "+timeSince(post_date)+" ago"
    }
}