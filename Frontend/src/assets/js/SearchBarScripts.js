// getting all required elements
let related_search_active = true;                                                                                      //fixme

$(document).ready(function () {
  if (related_search_active) {
    $('#search-bar').keyup(function (event) {
      let userData = event.target.value; //user enetered data
      let emptyArray = [];
      if (userData) {
        $("#search-icon").onclick = () => {
          search()
        }
        if (event.keyCode === 13) {
          search()
        }
        emptyArray = suggestions.filter((data) => {
          //filtering array value and user characters to lowercase and return only those words which are start with user enetered chars
          return data.toLocaleLowerCase().startsWith(userData.toLocaleLowerCase());
        });
        emptyArray = emptyArray.map((data) => {
          // passing return data inside li tag
          return `<li>${data}</li>`;
        });
        $(".search-input")[0].className = "search-input active"; //show autocomplete box
        showSuggestions(emptyArray);
        let allList = Array.from($('#suggestion-box li'));
        for (let i = 0; i < allList.length; i++) {
          //adding onclick attribute in all li tag
          allList[i].setAttribute("onclick", "select(this)");
        }
      } else {
        $(".search-input")[0].className = "search-input"; //hide autocomplete box
      }
    });
  }
})

function select(element) {
  $('#search-bar').val(element.textContent)
  search()
}

function showSuggestions(list) {
  let listData;
  let userValue;
  if (!list.length) {
    userValue = $('#search-bar').val();
    listData = `<li>${userValue}</li>`;
  } else {
    listData = list.join('');
  }
  $('#suggestion-box')[0].innerHTML = listData;
}

function deactivate_related_search() {
  related_search_active = !related_search_active
  console.log(related_search_active)
}
