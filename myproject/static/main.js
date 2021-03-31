var pathname = window.location.pathname; 
console.log(pathname)

var btnContainer = document.getElementById("myNavbar");
var btns = btnContainer.getElementsByClassName("nav-link");

if (pathname == '/') {
	btns[0].classList.add('active')
}
if (pathname == '/about_us') {
	btns[1].classList.add('active')
}
if (pathname == '/login') {
	btns[2].classList.add('active')
}
if (pathname == '/register') {
	btns[3].classList.add('active')
}
if (pathname == '/create') {
	btns[4].classList.add('active')
}
if (pathname == '/account') {
	btns[3].classList.add('active')
}
