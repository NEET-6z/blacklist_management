
document.addEventListener("DOMContentLoaded", function() {
    var postCodeField = document.getElementById("postcode");
    var addressField = document.getElementById("address");

    postCodeField.addEventListener("change", function() {
        var postCode = postCodeField.value;
        fetch(`/admin/blacklist/get_address/${postCode}/`, {
            method: 'GET',
          })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.text();  // テキストとしてレスポンスを取得する
          })
          .then(address => {
            if(address.length>=1) addressField.value = address
            console.log('Address:', address);
          })
          .catch(error => {
            console.error('Error fetching address:', error);
          });
    });
});