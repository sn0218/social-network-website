document.addEventListener('DOMContentLoaded', () => {

    // listen for the edit button
    document.addEventListener('click', event => {
        // find what was clicked on
        const element = event.target;

        // check if the user clicked on a edit button
        if (element.className === "btn btn-primary btn-sm border-0 px-3 edit-button") {
            // extract the button id
            const editButtonID = String(element.id);
            // extract the post id from button id
            const postID = editButtonID.substring(12);
            // execute the edit_post function
            edit_post(postID);
        }

        // check if the like text is clicked
        else if (element.className === "like-text") {
            // extract like text id
            const likeTextID = String(element.id);
            // extract post id from like text id
            const postID = likeTextID.substring(10);
            like(postID, element.value);
            
        }
    })

    
});

//first define your getCookie function
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


function like(post_id, likeVal) {
    console.log(likeVal)
    fetch(`/like/${post_id}`, {
        method: "POST",
        body: JSON.stringify({
            like: (likeVal === "like") ? true: false
        })
    })
    // convert post response to json form
    .then(response => response.json())
    .then(post => {
        // print result
        console.log(post);

        // update like-text
        const likeText = document.querySelector("#like-text-" + post_id );
        if (likeVal === "like") {
            likeText.value = "unlike";
            likeText.innerHTML = `Unlike`;
        } else {
            likeText.value = "like";
            likeText.innerHTML = `Like`;
        }
         
        // update like count
        const likeCount = document.querySelector("#like-count-" + post_id);
        fetch(`/likeCount/${post_id}`)
        .then(response => response.json())
        .then(result => {
            likeCount.innerHTML = `<i class="fa fa-thumbs-o-up" aria-hidden="true"></i> ${result.like_count}`;
        })

    })
    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });
    

    // stop form from submitting to stay in the sent mailbox view
    return false;
}


function edit_post(post_id) {
    // send a GET request to the server to get an email
    fetch(`/posts/${post_id}`)
    .then(response => response.json())
    .then(post => {
        // disable the view of post content and buttons
        document.querySelector('#post-' + post_id + '-content').style.display= 'none';
        document.querySelector('#buttons-' + post_id).style.display = 'none';

        // activate the edit view
        document.querySelector('#disable-post-' + post_id + '-content').style.display = 'block';

        // populated the post content 
        document.querySelector('#disable-post-' + post_id + '-content').innerHTML = `
        <form id="edit-post-form-${post.id}">
            <div class="form-group">
                <textarea class="form-control" id="new-post-content-${post.id}" rows="3">${post.content}</textarea>
            </div>
            <div class="d-flex justify-content-end align-items-center mt-2 ">
            <div class="p-2">
                <button type="button" id="cancel-button-${post.id}" class="btn btn-light btn-sm border-0 px-3">Cancel</button>
            </div>
            <div class="p-2">
                <button type="submit" id="save-button-${post.id}" class="btn btn-primary btn-sm border-0 px-3">Save</button>
            </div>        
            </div>
        </form> 
        `

        // if the save button is clicked, save the edited post
        document.querySelector('#edit-post-form-' + post_id).onsubmit = () => {
            // get csrftoken from browser's cookie
            let csrftoken = getCookie('csrftoken');

            submittedContent = document.querySelector('#new-post-content-' + post_id).value;

            // send a PUT request to server
            fetch(`/edit/${post_id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    id: post_id,
                    content: submittedContent
                }),
                headers: {"X-CSRFToken": csrftoken}
                
            })
            
            // put post response into json form
            .then(response => response.json())
            .then(result => {
                // Print result
                console.log(result);

                document.querySelector('#disable-post-' + post_id + '-content').style.display = 'none';
                document.querySelector('#post-' + post_id + '-content').style.display= 'block';
                document.querySelector('#buttons-' + post_id).style.display = 'block';

                // update the view of post's content
                document.querySelector('#post-' + post_id + '-content').innerHTML = submittedContent;
                  

            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
            
            // stop the form from submitting to stay in the current view
            return false;
        }
        
         // if the cancel button is clicked, display the orignal post content
         document.querySelector('#cancel-button-' + post_id).addEventListener('click', () => {
            document.querySelector('#disable-post-' + post_id + '-content').style.display = 'none';
            document.querySelector('#post-' + post_id + '-content').style.display= 'block';
            document.querySelector('#buttons-' + post_id).style.display = 'block';

        })
    })
}
