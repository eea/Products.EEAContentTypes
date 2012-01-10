function create_contact_info_local(theuser,thedomain,linktext) {
        var thecontact=(theuser + '@' + thedomain);
        thecontact='<A href="mailto:' + thecontact + '">' + linktext + '</a>';
        return thecontact;
}