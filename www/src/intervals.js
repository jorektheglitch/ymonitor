let href = location.href;
let base_url = href.slice(0, href.length-location.hash.length);
let intervals_container = document.getElementById("intervals");
let intervals = [
    ["day", "day"], ["week", "week"], 
    ["half of mounth", "halfmounth"], 
    ["all time", "all"]
];
for (let [name, keyword] of intervals){
    let link = document.createElement("a");
    link.innerText = name;
    link.setAttribute("href", `${base_url}#${keyword}`);
    link.className = "interval";
    intervals_container.append(link);
    intervals_container.innerHTML += " ";
};