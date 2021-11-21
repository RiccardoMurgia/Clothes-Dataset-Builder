function search() {
  const inputbox = $('#search-bar');
  const query = inputbox.val()
  inputbox.val('')
  if (query !== "") {
    if (query !== "Search" && is_changed(query)) {
      $.ajax({
        type: "GET",
        url: "http://127.0.0.1:5000/state_of_the_keys",
        contentType: "application/json",
        success: function (response) {
          console.log(response);
          if (JSON.parse(response).content === 'True') {
            reset_tabs()
            const images_tab = document.getElementById("images-tab")
            const tag_content = document.getElementById("tab-content")
            const new_li = document.createElement('li')
            new_li.role = "presentation"
            new_li.className = "active"
            new_li.id = query
            const new_a = document.createElement("a")
            new_a.href = "#" + query + "_"
            $(new_a).attr("aria-controls", query + "_")
            $(new_a).attr("role", "tab")
            $(new_a).attr("data-toggle", "tab")
            $(new_a).attr("aria-expanded", true)
            new_a.appendChild(document.createTextNode(query))
            new_li.appendChild(new_a)
            images_tab.appendChild(new_li)
            const new_div = document.createElement("div")
            $(new_div).attr("role", "tabpanel")
            new_div.className = "tab-pane active"
            new_div.id = query + "_"
            tag_content.appendChild(new_div)
            document.getElementById('footer').style.position = "absolute"
            add_spinner()
            build_the_gallery(query)
            $(".search-input")[0].className = "search-input"
          } else {
            window.alert('Error: Api Keys not initialize')
          }
        },
        error: function (err) {
          console.log(err);
        }
      })
    } else {
      alert("Research already done!")
    }
  } else {
    alert("Insert a query")
  }
}

function is_changed(query) {
  const list = document.getElementById("images-tab").getElementsByTagName('li')
  for (let i = 0; i < list.length; i++) {
    if (list[i].id === query) {
      return false
    }
  }
  return true
}

function reset_tabs() {
  let tabs = document.getElementById('images-tab').getElementsByTagName('li');
  let tabs_pane_id;
  if (tabs.length > 0) {
    for (let i = 0; i < tabs.length; i++) {
      if (tabs[i].className === "active") {
        tabs_pane_id = tabs[i].id + "_"
        document.getElementById(tabs_pane_id).className = "tab-pane"
        tabs[i].className = ""
      }
    }
  }
}

function add_spinner() {
  const row = document.createElement("div")
  row.className = "row"
  row.id = "spinner-row"
  const col = document.createElement("div")
  col.className = "col-md-3 bg"
  const loader = document.createElement("div")
  loader.className = "loader"
  loader.id = "loader-6"
  loader.appendChild(document.createElement("span"))
  loader.appendChild(document.createElement("span"))
  loader.appendChild(document.createElement("span"))
  loader.appendChild(document.createElement("span"))
  col.appendChild(loader)
  row.appendChild(loader)
  document.getElementById("images-container-row").appendChild(row)

}

function build_the_gallery(query) {
  const req = new XMLHttpRequest()
  let links
  const images_container = document.getElementById(query + "_")
  crete_close_btn(query)
  req.responseType = 'json'
  req.onload = function () {
    const jsonResponse = req.response
    // do something with jsonResponse
    for (let keywords in jsonResponse["content"])
      links = jsonResponse["content"][keywords]
    let new_row = document.createElement("div")
    let new_ul = document.createElement("ul")
    new_row.className = "row"
    new_ul.className = "gallery caption-3"
    for (let image = 0; image < links.length; image++) {
      let new_li = document.createElement("li")
      let new_figure = document.createElement("figure")
      let new_a = document.createElement("a")
      let new_img = document.createElement("img")
      let delete_btn = document.createElement("button")
      let i = document.createElement("i")
      new_li.id = "li" + image
      if (image < 21) {
        new_li.className = 'show'
      } else {
        new_li.className = 'hidden'
      }
      new_img.src = links[image]
      new_img.id = "image" + image.toString()
      new_img.alt = ""
      delete_btn.className = "btn delete-btn btn-md b"
      delete_btn.id = image.toString()
      delete_btn.onclick = delete_image
      $(delete_btn).attr("data-toggle", "tooltip")
      $(delete_btn).attr("data-placement", "left")
      $(delete_btn).attr("title", "Remove the image")
      i.className = "fa fa-trash"
      delete_btn.appendChild(i)
      new_a.appendChild(new_img)
      new_a.appendChild(delete_btn)
      new_figure.appendChild(new_a)
      new_li.appendChild(new_figure)
      new_ul.appendChild(new_li)
    }
    new_row.appendChild(new_ul)
    images_container.appendChild(new_row)
    const footer = document.getElementById('footer')
    footer.style.position = "relative"
    document.getElementById("spinner-row").remove()
    if (links.length > 20) {
      crate_show_more_results_btn(query)
    }
    create_clothes_detection_btn(query)
  };
  req.open('GET', 'http://127.0.0.1:5000/images?key=' + query, true)
  req.send(null)
}

function crete_close_btn(query) {
  const images_container = document.getElementById(query + "_")
  const close_btn = document.createElement("button")
  close_btn.type = "button"
  close_btn.className = "close"
  close_btn.addEventListener("click", close_tab)
  $(close_btn).attr("aria-label", "Close")
  const spn = document.createElement("span")
  $(spn).attr("aria-hidden", true)
  close_btn.appendChild(spn)
  spn.innerHTML = '&times;'
  images_container.appendChild(close_btn)
}

function create_clothes_detection_btn(query) {
  const images_container = document.getElementById(query + "_")
  const btn_row = document.createElement("div")
  const detection_btn = document.createElement("button")
  const label = document.createTextNode("Clothes detection")
  btn_row.className = "row"
  btn_row.id = "clothes-detection-btn-row"
  detection_btn.id = "clothes-detection-btn"
  detection_btn.className = "btn btn-primary"
  $(detection_btn).attr("data-target", "#build-your-dataset-menu")
  $(detection_btn).attr("data-toggle", "modal")
  detection_btn.appendChild(label)
  btn_row.appendChild(detection_btn)
  images_container.appendChild(btn_row)
}

function crate_show_more_results_btn(query) {
  const images_container = document.getElementById(query + '_')
  const show_more_btn = document.createElement("button")
  const btn_row = document.createElement("div")
  const btn_col = document.createElement("div")
  const label = document.createTextNode("Show more ")
  btn_row.className = "row"
  btn_row.id = "show-more-button-row"
  btn_col.className = "col-sm-12"
  show_more_btn.className = "btn btn-primary"
  show_more_btn.id = "more_btn"
  show_more_btn.type = "button"
  show_more_btn.value = "More"
  show_more_btn.appendChild(label)
  show_more_btn.addEventListener("click", show_more)
  btn_col.appendChild(show_more_btn)
  btn_row.appendChild(btn_col)
  images_container.appendChild(btn_row)
}

function close_tab() {
  let tabs = document.getElementById("images-tab").getElementsByTagName("li");
  let tab_content = document.getElementById("tab-content")
  let active_index = 0
  for (let i = 0; i < tabs.length; i++) {
    if (tabs[i].className === "active")
      active_index = i
  }
  let tab_id = tabs[active_index].id
  let tab_pane = document.getElementById(tab_id + "_")
  remove_links(tab_id)
  tab_content.removeChild(tab_pane)
  document.getElementById("images-tab").removeChild(tabs[active_index])
  if (tabs.length > 0) {
    if (active_index === 0) {
      active_index = 0
    } else {
      active_index -= 1
    }
    tabs[active_index].className = "active"
    active_index = tabs[active_index].id
    tab_pane = document.getElementById(tabs[active_index].id + "_")
    tab_pane.className = "tab-pane active"
  }
  if (tabs.length === 0) {
    document.getElementById("footer").style.position = "absolute"
  }
}

function remove_links(query) {
  $.ajax({
    type: "DELETE",
    url: "http://127.0.0.1:5000/keywords?key=" + query,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
    },
    error: function (err) {
      console.log(err);
    }
  })
}

function clothes_detection() {
  setTimeout(get_progress_state, 2000)
  let datasetName = 'MyDataset'
  if (document.getElementById("recipient-name").value !== "")
    datasetName = document.getElementById("recipient-name").value
  if (document.getElementById('message_box').className === 'show')
    document.getElementById('message_box').className = 'hidden'
  document.getElementById("progress_bar").className = "progress show"
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:5000/clothes_detected?key=" + datasetName,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
    },
    error: function (err) {
      console.log(err);
    }
  })
}

function get_progress_state() {
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:5000/progress_state",
    contentType: "application/json",
    success: function (response) {
      document.getElementById('progress_percentage').innerHTML = ((Math.round(JSON.parse(response).content) * 100) / 100).toString() + "%"
      document.getElementById('fill_percentage').style.width = (JSON.parse(response).content).toString() + "%"
      if (JSON.parse(response).content < 100) {
        setTimeout(get_progress_state, 2000)
      } else {
        setTimeout(function () {
          document.getElementById('progress_bar').className = "progress hidden"
          document.getElementById('progress_percentage').innerHTML = "0%"
          document.getElementById('fill_percentage').style.width = "0%"
          //document.getElementById("close_modal_btn").click()
          document.getElementById('message').innerHTML = 'Detection completed. Your Dataset is now available in the Dataset-viewer section.'
          document.getElementById('message_box').className = 'show'
        }, 1000)
      }
    },
    error: function (err) {
      console.log(err);
    }
  })
}

function close_detection_modal() {
  document.getElementById("recipient-name").value = ""
  document.getElementById("recipient-name").setAttribute('placeholder', 'MyDataset')
  document.getElementById('message_box').className = 'hidden'
  document.getElementById('message').innerHTML = ""
}

function delete_image() {
  const button_id = this.id
  const img_id = "image" + button_id
  let link
  let hidden_images = Array.from($('.tab-pane.active .hidden'))
  let li_images = Array.from($('.tab-pane.active li'))
  let images = Array.from($('.tab-pane.active img'))
  for (let i = 0; i < images.length; i++) {
    if (images[i].id === img_id) {
      link = images[i].src
      li_images[i].remove()
    }
  }
  $.ajax({
    type: "DELETE",
    url: "http://127.0.0.1:5000/delete_link?key=" + link,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
    },
    error: function (err) {
      console.log(err);
    }
  })
  if (hidden_images.length - 1 === 0) {
    $('.tab-pane.active #more_btn').remove()
  }
  if (li_images.length - 1 === 0) {
    $('.tab-pane.active .close').click()
  }
  if (hidden_images.length !== 0)
    hidden_images[0].className = "show"
}

function show_more() {
  let hidden_images = Array.from($('.tab-pane.active .hidden'))
  if (hidden_images.length !== 0) {
    if (hidden_images.length < 20) {
      for (let i = 0; i < hidden_images.length; i++)
        hidden_images[i].className = "show"
    } else {
      for (let i = 0; i < 20; i++)
        hidden_images[i].className = "show"
    }
  }
  hidden_images = Array.from($('.tab-pane.active .hidden'))
  if (hidden_images.length === 0) {
    $('.tab-pane.active #more_btn').remove()
  }
}

function hover(element) {
  element.setAttribute('src', 'assets/images/logo1.png');
}

function un_hover(element) {
  element.setAttribute('src', 'assets/images/logo.png');
}

function save_search_options() {
  const number = document.getElementById("inputNumber").value
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:5000/number_of_links?value=" + number,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
    },
    error: function (err) {
      console.log(err);
    }
  })

}

function close_change_password_modal() {
  document.getElementById("recipient-new-password").value = ""
  document.getElementById("recipient-new-password-copy").value = ""
  document.getElementById("message_box").className = "hidden"
  document.getElementById("recipient-new-password").style.borderColor = "#ccc"
  document.getElementById("recipient-new-password-copy").style.borderColor = "#ccc"

}

function save_password() {
  let password = document.getElementById("recipient-new-password").value
  let password_copy = document.getElementById("recipient-new-password-copy").value
  if (document.getElementById("message_box").className === "show") {
    document.getElementById("recipient-new-password-copy").style.borderColor = "#ccc"
  }
  if (Boolean(password) && Boolean(password_copy)) {
    if (password === password_copy) {                                                                                   //Todo check requirements
      //salva la password                                                                                             //Todo Save the Password
      document.getElementById('message').textContent = "Your new password has been updated"
    } else if (password !== password_copy) {
      document.getElementById('message').textContent = "The passwords do not match"
      document.getElementById("recipient-new-password-copy").style.borderColor = "red"
    }
  } else if (Boolean(password)) {
    document.getElementById('message').textContent = "Confirm Your Password"
    document.getElementById("recipient-new-password-copy").style.borderColor = "red"
  } else {
    document.getElementById('message').textContent = "Insert a new password"
    document.getElementById("recipient-new-password").style.borderColor = "red"
  }
  document.getElementById("message_box").className = "show"
}


function save_api_keys() {
  let input_form_list = Array.from($('.key-form .form-control.my-active'))
  let full_fields = true
  for (let i = 0; i < input_form_list.length; i++) {
    if (!Boolean(input_form_list[i].value)) {
      full_fields = false
      input_form_list[i].style.borderColor = "red"
      document.getElementById('key-form-message-box').className = 'show'
      document.getElementById('key-form-message-box').textContent = 'Some fields are empty'
    } else {
      input_form_list[i].style.borderColor = "#ccc"
    }
  }
  if (full_fields) {
    if (document.getElementById('key-form-message-box').className === 'show') {
      for (let i = 0; i < input_form_list.length; i++) {
        input_form_list[i].style.borderColor = "#ccc"
        document.getElementById('key-form-message-box').className = 'hidden'
      }
    }
    $.ajax({
      type: "GET",
      url: "http://127.0.0.1:5000/api_keys" + create_args_api_keys(),
      contentType: "application/json",
      success: function (response) {
        console.log(response);
      },
      error: function (err) {
        console.log(err);
        window.alert("Error: keys not initialized.")
      }
    })
  }
}

function deactivate_api(btn) {
  let disable_search_engine_name = btn.id.split("-")[1]
  let disable_key_form_name = disable_search_engine_name + "-api-key-form"
  let disable_engine_id_form_name = disable_search_engine_name + "-engine-id-form"
  let input_form_list = Array.from($('.key-form .form-control'))
  if (btn.className === 'btn btn-default') {
    if (Array.from($('.btn.btn-default.my-disabled')).length === 0) {
      btn.className = 'btn btn-default my-disabled'
      for (let i = 0; i < input_form_list.length; i++) {
        if (input_form_list[i].id === disable_key_form_name || input_form_list[i].id === disable_engine_id_form_name) {
          input_form_list[i].className = "form-control my-disabled"
          if (input_form_list[i].borderColor !== "#ccc")
            input_form_list[i].style.borderColor = "#ccc"
          document.getElementById('key-form-message-box').className = 'hidden'

          //fixme
        }
      }
    } else {
      window.alert('The search operation requires at least one key')
    }
  } else {
    btn.className = 'btn btn-default'
    for (let i = 0; i < input_form_list.length; i++) {
      if (input_form_list[i].id === disable_key_form_name || input_form_list[i].id === disable_engine_id_form_name) {
        input_form_list[i].className = "form-control my-active"
      }
    }
  }
}

function create_args_api_keys() {
  let google_api_key, google_engine_id, flickr_api_key, flickr_engine_id, url_args
  let disabled_btn_list = Array.from($('.btn.btn-default.my-disabled'))
  if (disabled_btn_list.length === 0) {
    google_api_key = document.getElementById('google-api-key-form').value
    google_engine_id = document.getElementById('google-engine-id-form').value
    flickr_api_key = document.getElementById('flickr-api-key-form').value
    flickr_engine_id = document.getElementById('flickr-engine-id-form').value
    url_args = "?code=" + "0" + "&google_key=" + google_api_key + "&google_engine_id=" + google_engine_id +
      "&flickr_key=" + flickr_api_key + "&flickr_engine_id=" + flickr_engine_id
  } else {
    if (disabled_btn_list[0].id === 'deactivate-google') {
      flickr_api_key = document.getElementById('flickr-api-key-form').value
      flickr_engine_id = document.getElementById('flickr-engine-id-form').value
      url_args = "?code=" + "1" + "&flickr_key=" + flickr_api_key + "&flickr_engine_id=" + flickr_engine_id
    } else {
      google_api_key = document.getElementById('google-api-key-form').value
      google_engine_id = document.getElementById('google-engine-id-form').value
      url_args = "?code=" + "2" + "&google_key=" + google_api_key + "&google_engine_id=" + google_engine_id
    }
  }
  return url_args
}


function build_dataset_viewer(response) {
  if (response["content"] !== 'No datasets available') {
    build_dataset_viewer_menu(response)
    build_clothes_viewer(response)
  } else                                                               //dataset not available
    console.log(response.content)
}

function build_dataset_viewer_menu(response) {
  let filter_menu = document.getElementById("filter-menu")
  let dataset_ul = document.createElement("ul")
  dataset_ul.className = "list-group list-group-flush"
  dataset_ul.id = "dataset-list"
  let dataset_li, dataset_div, dataset_input, dataset_label, event_ul, download_a ,download_btn, download_icon,
  delete_btn, delete_icon;
  for (let dataset in response["content"]) {
    dataset_li = document.createElement("li")
    dataset_div = document.createElement("div")
    dataset_input = document.createElement("input")
    dataset_label = document.createElement("label")
    download_a = document.createElement("a")
    download_btn = document.createElement("button")
    download_icon = document.createElement("i")

    delete_btn = document.createElement("button")
    delete_icon = document.createElement("i")

    dataset_input.onclick = show_events
    dataset_li.className = "list-group-item"
    dataset_div.className = "custom-control custom-checkbox"
    dataset_input.type = "checkbox"
    dataset_input.className = "custom-control-input"
    dataset_label.className = "custom-control-label"
    download_btn.className= "btn btn-default my-btn"
    delete_btn.className = "btn btn-default my-btn"
    $(download_btn).attr("data-toggle", "tooltip")
    $(download_btn).attr("data-placement", "left")
    $(download_btn).attr("title", "Download")
    $(delete_btn).attr("data-toggle", "tooltip")
    $(delete_btn).attr("data-placement", "left")
    $(delete_btn).attr("title", "Delete")
    download_icon.className = "fa fa-download"
    delete_icon.className = "fa fa-trash"
    delete_btn.id = dataset
    dataset_input.id = dataset
    dataset_label.setAttribute("for", dataset)
    dataset_label.appendChild(document.createTextNode(dataset))
    event_ul = document.createElement("ul")
    event_ul.className = "list-group hidden"
    event_ul.id = dataset + "-eventList"
    download_a.href = "http://127.0.0.1:5000/download_dataset?key=" + dataset
    download_a.id = dataset
    download_a.download="Dataset"
    delete_btn.onclick= delete_dataset
    for (let event in response["content"][dataset]) {
      if (event !== 'info') {
        let event_li = document.createElement("li")
        let event_input = document.createElement("input")
        let event_label = document.createElement("label")
        event_li.className = "list-group-item event-item"
        event_input.type = "checkbox"
        event_input.className = "custom-control-input"
        event_input.id = dataset + "/" + event
        event_input.onclick = show_clothes
        event_label.className = "custom-control-label"
        event_label.setAttribute("for", event)
        event_label.appendChild(document.createTextNode(event))
        event_li.appendChild(event_input)
        event_li.appendChild(event_label)
        event_ul.appendChild(event_li)
      }
    }
    dataset_div.appendChild(dataset_input)
    dataset_div.appendChild(dataset_label)
    download_btn.appendChild(download_icon)
    delete_btn.appendChild(delete_icon)
    download_a.appendChild(download_btn)
    dataset_div.appendChild(download_a)
    dataset_div.appendChild(delete_btn)
    dataset_div.appendChild(event_ul)
    dataset_li.appendChild(dataset_div)
    dataset_ul.appendChild(dataset_li)
    filter_menu.appendChild(dataset_ul)
  }

}

function show_events() {
  let event_list_id = this.id.split("-")[0] + "-eventList"
  if (document.getElementById(event_list_id).classList.contains("hidden")) {
    document.getElementById(event_list_id).classList.remove("hidden")
  } else {
    document.getElementById(event_list_id).classList.add("hidden")
  }
}

function show_clothes() {
  let check_box_id = this.id
  let hidden_li = Array.from($('.gallery.caption-3 li'))
  let li_id;
  for (let i = 0; i < hidden_li.length; i++) {
    li_id = hidden_li[i].id
    if (li_id.includes(check_box_id)) {
      if (hidden_li[i].classList.contains('hidden')) {
        hidden_li[i].classList.remove('hidden')
        document.getElementById('footer').style.position = "relative"
      } else {
        hidden_li[i].classList.add("hidden")
        if (Array.from($('.gallery.caption-3 li')).length === Array.from($('.gallery.caption-3 .hidden')).length) {
          document.getElementById('footer').style.position = "absolute"
        }
      }
    }
  }
}

function build_clothes_viewer(response) {
  let clothes_viewer = document.getElementById("clothes_viewer")
  let new_figure, new_img, new_li, new_a, new_btn, i, path, path_list, li_id;
  let count = 0
  for (let dataset in response["content"]) {
    for (let image in response["content"][dataset]["info"]) {
      path = response["content"][dataset]["info"][image]['path']
      path_list = path.split("/")
      li_id = path_list[2] + "/" + path_list[5] + "/" + count
      count++
      new_li = document.createElement("li")
      new_figure = document.createElement('figure')
      new_a = document.createElement('a')
      new_img = document.createElement("img")
      new_btn = document.createElement("button")
      i = document.createElement("i")
      new_btn.className = "btn delete-btn btn-md b"
      new_btn.id = path
      new_li.id = li_id
      new_li.className = "hidden"
      new_btn.onclick = delete_clothes_image
      $(new_btn).attr("data-toggle", "tooltip")
      $(new_btn).attr("data-placement", "left")
      $(new_btn).attr("title", "Remove the image")
      new_img.src = "data:image/jpeg;base64," + response["content"][dataset]["info"][image]['base64 encoding']
      i.className = "fa fa-trash"
      new_btn.appendChild(i)
      new_a.appendChild(new_img)
      new_a.appendChild(new_btn)
      new_figure.appendChild(new_a)
      new_li.appendChild(new_figure)
      clothes_viewer.appendChild(new_li)
    }
  }
}

function delete_clothes_image() {
  let path = this.id
  document.getElementById(this.id).parentElement.parentElement.parentElement.remove()
  $.ajax({
    type: "DELETE",
    url: "http://127.0.0.1:5000/" + "deleted_clothes?path=" + path,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
    },
    error: function (err) {
      console.log(err);
    }
  })
}

function delete_dataset(){
  const id = this.id
  $.ajax({
    type: "DELETE",
    url: "http://127.0.0.1:5000/" + "delete_dataset?dataset=" + id,
    contentType: "application/json",
    success: function (response) {
      console.log(response);
      document.getElementById(id).parentElement.parentElement.remove()
    },
    error: function (err) {
      console.log(err);
    }
  })
}


