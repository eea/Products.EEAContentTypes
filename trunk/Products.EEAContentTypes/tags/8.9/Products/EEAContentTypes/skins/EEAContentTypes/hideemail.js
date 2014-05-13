function create_contact_info_local(theuser,thedomain,linktext) {
        var thecontact=(theuser + '@' + thedomain);
        thecontact='<A href="mailto:' + thecontact + '">' + linktext + '</a>';
        return thecontact;
}


jQuery(function($){
    $(".protectEmail").each(function(){
        // entry are expected to contain 3 values
        //  1. email address, 2. domain 3. text content for link
        var text = this.innerHTML.split(',');
        this.href = 'mailto:' + text[0] + '@' + text[1];
        this.innerHTML = text[2];
        this.className = this.className.replace("hiddenStructure", '');
    });
});
