<script>
function inviteFBFriends() {
  FB.ui({
    method: 'apprequests',
    message: '{{user_firstname}} has invited you to join {{group.name}} at We Share A.',
    data: 'tracking information for the user'
  },  function (response) {
         console.log(response);
    	 if (response.request && response.to) {
             var req_ids = [];
             for(i=0; i<response.to.length; i++) {
             	var temp = response.request + '_' + response.to[i];
             	req_ids.push(temp);
             }
    	     $.post("{% url invite_facebook group.id %}", { user_app_requests: req_ids }, //jquery post to send csv list of invite ids to add participants view
    	            function(data){ window.location.reload(true) });  //reloads the page should reload the div only
         } else {
    	    //Do something if they don't send it.
    	 }
      })
    }
</script>