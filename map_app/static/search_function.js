
function liveSearch() {
  // Declare variables
  var input, filter, list, item, bird, i, txtValue;
  input = document.getElementById('searchInput');
  filter = input.value.toUpperCase();
  list = document.getElementById("birdList");
  item = list.getElementsByClassName('list-group-item');

  console.log("Item:" + item);
  console.log(item);

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < item.length; i++) {
    bird = item[i];

    console.log("Bird:" + bird);

    txtValue = bird.textContent || bird.innerText;
    
    console.log("txtValue:" + txtValue);

    if (txtValue.toUpperCase().indexOf(filter) > -1) {
        item[i].style.display = "";
    } else {
        item[i].style.display = "none";
    }
  }
}
