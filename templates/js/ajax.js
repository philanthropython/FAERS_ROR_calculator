function post_greeting() {
  $.ajax({
    type: 'POST',
    url: '/levels',
    data: '',
    contentType: 'application/json',
    success: function (data) {
      const drug_list = JSON.parse(data.ResultSet).drug_list
      const reac_list = JSON.parse(data.ResultSet).reac_list
      document.getElementById('greeting').innerHTML = drug_list
      document.getElementById('greeting_image').src = reac_list
    }
  })
}
