let count = 0
function checkCredentials() {
    // package data in a JSON object
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    var data_d = {'email': email, 'password': password}
    console.log('data_d', data_d)

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processlogin",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              if (retruned_data['success'] == 1)
              {
                // travel to home page
                window.location.href = "/popup";
              }else
              {
                // increment count
                count = count + 1;
            
              document.getElementById("count").textContent = "Failed attempts: " + count;
              }
              
            }        
    });
}

function createUser() 
{
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  var data_d = {'email': email, 'password': password}
  console.log('data_d', data_d)

  // SEND DATA TO SERVER VIA jQuery.ajax({})
  jQuery.ajax({
    url: "/processsignup",
    data: data_d,
    type: "POST",
    success:function(retruned_data){
          retruned_data = JSON.parse(retruned_data);
          if (retruned_data['success'] == 1)
          {
            // travel to home page
            window.location.href = "/login";
          }else
          {
        
          document.getElementById("count").textContent = 'Email already has an account';
          }
          
        }        
});
}