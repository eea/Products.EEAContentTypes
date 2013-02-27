function ContentCreationPopup(){
    this.set_creators();
}

ContentCreationPopup.prototype.fix_form_widgets = function(el){

    // init tinymce edit fields
    jq('.mce_editable', el).each(function(){
        //ids can be repeated because of duplicated field names
        //same field can exist in the main page and also in the popup dialog
        if (jq(this).attr('id').indexOf('p0') === 0) {
            return;
        }
        var id = "p0" + Math.random().toString().replace('.', '') + jq(this).attr('id');
        jq(this).attr('id', id);
        //delete InitializedTinyMCEInstances[id];
        var config = new TinyMCEConfig(id);
        // TODO: fix the editor sizes
        //config.widget_config.editor_height = 800;
        //config.widget_config.editor_width = 630;
        //config.widget_config.autoresize = true;
        //config.widget_config.resizing = true;
        //config.widget_config.resizing_use_cookie = false;
        //delete InitializedTinyMCEInstances[id];
        config.init();
    });

    //set the tags widget
    var widgets = jq('.ArchetypesKeywordWidget');
    if(widgets.length){
        widgets.eeatags();
    }

    // fix organisations widget
  //jq(".dummy-org-selector", el).each(function(){
  //    var id = jq(this).attr('id');
  //    if (id.indexOf('p0') !== 0) {
  //        id = "p0" + Math.random().toString().replace('.', '').substr(2,6) + jq(this).attr('id');
  //        jq(this).attr('id', id);
  //        //new SelectAutocompleteWidget(jq("#" + id));
  //    }
  //});

    // other fixes to include: 
    // geographical coverage
    // organisations widget
    // temporal coverage
    // reference system widget has no label
    // geographical accuracy, contact person and disclaimer are not tinymce!?

};

ContentCreationPopup.prototype.schemata_ajaxify = function(el){

    var self = this;

    self.fix_form_widgets(el);
    //set_actives();

    jq("form", el).submit(
    function(e){
      tinyMCE.triggerSave();
      var form = this;

      var inputs = [];
      jq(".widgets-list .widget-name").each(function(){
        inputs.push(jq(this).text());
      });

      var data = "";
      data = jq(form).serialize();
      // data += "&_active_region=" + active_region;
      data += "&form_submit=Save&form.submitted=1";

      jq.ajax({
        "data": data,
        url: this.action,
        type:'POST',
        cache:false,
        // timeout: 2000,
        error: function() {
          alert("Failed to submit");
        },
        success: function(r) {
          jq(el).html(r);
          self.schemata_ajaxify(el);
          return false;
        }
      });
      return false;
    });
};

ContentCreationPopup.prototype.set_creators = function(){
    var self = this;
    jq('a.new_content_creator').click(function(){
        var link = jq(this).attr('href');
        var portal_type = "";
        var title = "Edit new " + portal_type;    // should insert portal type here
        var options = {
          'width':1000,
          'height':700
        };
        self.dialog_edit(link, title, 
                function(text, status, xhr){
                    self.schemata_ajaxify(jq("#dialog-inner"));   //set someid
                },
                options);

        return false;
    });
};

ContentCreationPopup.prototype.dialog_edit = function(url, title, callback, options){
      // Opens a modal dialog with the given title

      var self = this;
      options = options || {
        'height':null,
        'width':1000
      };
      var target = jq('#dialog_edit_target');
      jq("#dialog-inner").remove();     // temporary, apply real fix
      jq(target).append("<div id='dialog-inner'></div>");
      window.onbeforeunload = null; // this disables the form unloaders
      jq("#dialog-inner").dialog({
        modal         : true,
        width         : options.width,
        minWidth      : options.width,
        height        : options.height,
        minHeight     : options.height,
        'title'       : title,
        closeOnEscape : true,
        buttons: {
          'Save':function(e){
            var button = e.target;
            jq("#dialog-inner form").trigger('submit');
          },
          'Cancel':function(e){
            jq("#dialog-inner").dialog("close");
          }
        },
        beforeclose:function(event, ui){ return true; }
      });

      jq.ajax({
        'url':url,
        'type':'GET',
        'cache':false,
        'success': function(r){
          jq("#dialog-inner").html(jq(r));
          //set_inout(jq("#archetypes-fieldname-themes"));
          callback();
        }
      });
};

var contentcreation_popup = new ContentCreationPopup();

function close_dialog(info) {                                                                                                                                        
    var popups = [];
    jq(".indicators_relations_widget").each(function(){ 
        var fieldname = $(".metadata .fieldName", this).text();
        var realfieldname = $(".metadata .realFieldName", this).text();
        var widget_dom_id = $(".metadata .widget_dom_id", this).text();
        if (!widget_dom_id) {
          return false;
        }
        var popup = jq('#' + widget_dom_id).get(0)._widget; 
        popups.push(popup);
    });


   if (info.search('http://') !== -1) {                                                                                                                              
       jq("#dialog-inner").dialog("close");                                                                                                                          
       if (typeof(window.popup) !== "undefined") {
           jq(window.popup.events).trigger('EEA-REFERENCEBROWSER-BASKET-ADD', {url:info});                                                                               
       } else {
        if (!popups.length) {
            alert("could not get eea.reference popup");
        } else {
            jq(popups).each(function(){
                jq(this.events).trigger('EEA-REFERENCEBROWSER-BASKET-ADD', {url:info});
            });
        }
       }
   } else {                                                                                                                                                          
       // compatibility with eea.indicators                                                                                                                          
       reload_region($("#"+region));                                                                                                                                 
       jq("#dialog-inner").dialog("close");                                                                                                                          
   }                                                                                                                                                                 
}

//jq("#content-creation-portlet legend").show();
