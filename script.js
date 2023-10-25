
document.getElementById("addbutton").onclick=function(){
    let  list = document.getElementById("todo").value;
    document.getElementById("checkbox").innerHTML=list;
}

const checklist = document.getElementById('listdiv');

checklist.addEventListener('click', (event) => {
  if (event.target.tagName === 'INPUT') {
    event.target.nextElementSibling.classList.toggle('checked');
  }
});