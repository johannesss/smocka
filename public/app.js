new Vue({
  el: '#app',

  watch: {
    'form.status_code': function (code) {
      if (code === null) {
        this.showStatusCodeSuggestions();
      }
    }
  },

  computed: {
    filteredStatusCodes: function () {
      return this.statusCodes.filter(function (obj) {
        return obj.text.toString()
          .toLowerCase()
          .indexOf(this.statusCodeFilter.toLowerCase()) >= 0
      }.bind(this));
    }
  },

  data: function () {
    return {
      labelPosition: 'on-border',

      editor: null,
      statusCodes: [],
      contentTypes: [],
      statusCodeFilter: '',

      fetchingSettings: null,
      loading: false,

      form: {
        body: '',
        content_type: 'application/json',
        status_code: null,
        ttl: 0
      },

      responseLink: null,
      responseLinkCopySuccess: null
    }
  },

  methods: {
    submit: function () {
      var config = {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };

      var self = this;
      self.responseLink = null;
      self.loading = true;

      axios.post('/response', this.form, config)
        .then(function (response) {
          self.responseLink = window.location.origin + response.data.url;
        })
        .catch(function (err) {
          console.error('Could not save the response.', err);
          self.$buefy.snackbar.open({
            position: 'is-bottom',
            message: 'Something went wrong saving the response!',
            type: 'is-danger',
            indefinite: true
          });
        })
        .finally(function () {
          self.loading = false;
        });
    },

    showStatusCodeSuggestions() {
      this.$nextTick(function () {
        this.$refs.statusCode.$el.querySelector('input').blur();
        setTimeout(function () {
          this.$refs.statusCode.focus();
        }.bind(this));
      });
    },

    setStatusCode: function (obj) {
      if (obj === null) {
        this.form.status_code = null;
      } else {
        this.form.status_code = obj.value;
      }
    },

    handleStatusCodeBlur: function () {
      var self = this;
      setTimeout(function () {
        var statusCode = self.statusCodes.filter(function (obj) {
          return obj.value === self.form.status_code;
        });

        if (statusCode.length === 0) {
          self.statusCodeFilter = '';
          self.form.status_code = null;
        }
      }, 300);
    },

    setDefaultSelectedStatusCode: function () {
      var STATUS_CODE_200 = this.statusCodes.filter(function (obj) {
        return obj.value === 200;
      })[0];
      this.$refs.statusCode.setSelected(STATUS_CODE_200);
    },

    loadSettings: function () {
      this.fetchingSettings = true;

      axios.get('/settings')
        .then(function (response) {
          this.statusCodes = response.data.status_codes;
          this.contentTypes = response.data.content_types;

          this.setDefaultSelectedStatusCode();
        }.bind(this))
        .catch(function (err) {
          console.log(err);
        })
        .finally(function () {
          this.fetchingSettings = false;
        }.bind(this));
    },

    initEditor: function () {
      this.editor = ace.edit(this.$refs.body, {
        mode: "ace/mode/json",
        selectionStyle: "text",
        highlightActiveLine: false,
        showPrintMargin: false,
        showGutter: false
      });

      this.editor.renderer.setScrollMargin(10, 10);

      this.editor.session.on('change', function () {
        this.form.body = this.editor.getValue();
      }.bind(this));
    },

    setEditorMode: function (contentType) {
      var modesMap = {
        'text/html': 'html',
        'application/json': 'json',
        'text/xml': 'xml',
        'text/css': 'css'
      };

      if (modesMap[contentType]) {
        this.editor.setOption('mode', 'ace/mode/' + modesMap[contentType]);
      } else {
        this.editor.setOption('mode', 'ace/mode/text');
      }
    },

    copyResponseLink: function () {
      this.responseLinkCopySuccess = null;

      if (this.copyToClipboard(this.responseLink)) {
        this.responseLinkCopySuccess = true;
      } else {
        this.responseLinkCopySuccess = false;
      }

      setTimeout(function () {
        this.responseLinkCopySuccess = null;
      }.bind(this), 1000);
    },

    copyToClipboard: function (text) {
      if (window.clipboardData && window.clipboardData.setData) {
        // Internet Explorer-specific code path to prevent textarea being shown while dialog is visible.
        return clipboardData.setData("Text", text);

      }
      else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
        var textarea = document.createElement("textarea");
        textarea.textContent = text;
        textarea.style.position = "fixed";  // Prevent scrolling to bottom of page in Microsoft Edge.
        document.body.appendChild(textarea);
        textarea.select();
        try {
          return document.execCommand("copy");  // Security exception may be thrown by some browsers.
        }
        catch (ex) {
          console.warn("Copy to clipboard failed.", ex);
          return false;
        }
        finally {
          document.body.removeChild(textarea);
        }
      }
    }
  },

  created: function () {
    this.loadSettings();
  },

  mounted: function () {
    this.initEditor();
  }

});