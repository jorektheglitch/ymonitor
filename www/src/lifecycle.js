let href = location.href;
const base_url = href.slice(0, href.length - location.hash.length);
const intervals = [
	["day", "day"], ["week", "week"],
	["half of mounth", "halfmounth"],
	["all time", "all"]
];
let intervals_container = document.getElementById("intervals");

for (let [name, keyword] of intervals) {
	let link = document.createElement("a");
	link.innerText = name;
	link.setAttribute("href", `${base_url}#${keyword}`);
	link.className = "interval";
	intervals_container.append(link);
	intervals_container.innerHTML += " ";
};


const sortNum = (a, b) => parseInt(a) - parseInt(b);
const table = document.getElementById("shifts");
const cleanTable = table.innerHTML;

function getKeywordFromHash() {
	let hash = location.hash.substring(1);
	if (["day", "week", "halfmounth", "all"].includes(hash)) {
		return hash;
	} else {
		return "day"
	};
};

async function updateTableContent() {
	let path = `/api/${getKeywordFromHash()}/by_hour`;
	const res = await fetch(path);
	const data = await res.json();
	const heads = Object.keys(data).sort(sortNum);
	table.innerHTML = cleanTable;
	if (!Object.keys(data).length) {
		let messageRow = document.createElement("tr");
		let message = document.createElement("td");
		message.innerText = "There was no shifts. Stability!";
		message.className = "center_t empty_msg";
		message.colSpan = "2";
		messageRow.append(message);
		table.append(messageRow);
	};
	for (const hour of heads) {
		const el = document.createElement("tr");
		const date = new Date((hour | 0) * 1000);
		let dtField = document.createElement("td");
		dtField.innerText = `${date.format("dd.mm.yyyy HH")}:00`;
		let shiftsField = document.createElement("td");
		shiftsField.innerText = `${data[hour]}`;
		el.append(dtField);
		el.append(shiftsField);
		table.append(el);
	};
};

function updateTable() {
	updateTableContent().then(
		(success) => {
			delErr();
		},
		(error) => {
			showErr(error);
		});
};

function showErr(error) {
	let container = document.getElementsByClassName("error_message")[0];
	if (!container) {
		let container = document.createElement("h6");
		container.className = "error_message center_t";
		container.append(document.createTextNode(`\
            Can't fetch shifts from server.\n\
            Reason: ${error}.\n\n\
            Please wait or try to reload this page.\n`
		));
		table.before(container);
	};
	console.error(error);
}

function delErr() {
	let container = document.getElementsByClassName("error_message")[0];
	if (container) {
		container.remove();
	};
};

updateTable();

for (let hashLink of document.getElementsByClassName("interval")) {
	hashLink.onclick = () => {
		setTimeout(updateTable, 10);
	};
};

setInterval(updateTable, 5 * 60 * 1000); //one update per 5 minutes