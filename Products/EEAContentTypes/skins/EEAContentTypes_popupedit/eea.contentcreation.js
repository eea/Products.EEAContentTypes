function ContentCreationPopup(){
    this.set_creators()
}

ContentCreationPopup.prototype.init_tinymce = function (el){
  // init tinymce edit fields
  jq('.mce_editable', el).each(function(){
    //ids can be repeated because of duplicated field names
    //same field can exist in the main page and also in the popup dialog
    var id = "popup-" + jq(this).attr('id');
    jq(this).attr('id', id);
    delete InitializedTinyMCEInstances[id];
    var config = new TinyMCEConfig(id);
    // TODO: fix the editor sizes
    config.widget_config.editor_height = 800;
    config.widget_config.editor_width = 630;
    config.widget_config.autoresize = true;
    config.widget_config.resizing = true;
    config.widget_config.resizing_use_cookie = false;
    //delete InitializedTinyMCEInstances[id];
    config.init();
  });
}

ContentCreationPopup.prototype.schemata_ajaxify = function(el){

    var self = this;
    //set_actives();
    self.init_tinymce(el);

    //set the tags widget
    var widgets = jq('.ArchetypesKeywordWidget');
    if(widgets.length){
    widgets.eeatags();
    }

    // other fixes to include: 
    // geographical coverage
    // organisations widget
    // temporal coverage
    // reference system widget has no label
    // geographical accuracy, contact person and disclaimer are not tinymce!?

    jq("form", el).submit(
    function(e){
      //block_ui();
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
          //unblock_ui();
          alert("Failed to submit");
        },
        success: function(r) {
          jq(el).html(r);
          self.schemata_ajaxify(el);
          //unblock_ui();
          return false;
        }
      });
      return false;
    });
}

ContentCreationPopup.prototype.set_creators = function(){
    var self = this;
    jq('a.new_content_creator').click(function(){
        //block_ui();
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
}

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
}

var contentcreation_popup = new ContentCreationPopup();

function close_dialog(info) {
   if (info.search('http://') !== -1) {
       jq("#dialog-inner").dialog("close");
       jq(window.popup.events).trigger('EEA-REFERENCEBROWSER-BASKET-ADD', {url:info});
   } else {
       // compatibility with eea.indicators
       reload_region($("#"+region));
       jq("#dialog-inner").dialog("close");
   }
}
