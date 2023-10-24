function addtolist() {
  var input = document.getElementById("addlist");
  var text = input.value.trim();

  if (text !== "") {
    var list = document.getElementById("lists");
    var listItem = document.createElement("li");
    listItem.textContent = text;
    listItem.classList.add("lists-item");

    listItem.addEventListener("click", function () {
      listItem.classList.toggle("checked");
    });

    list.appendChild(listItem);
    input.value = "";
  }
}
