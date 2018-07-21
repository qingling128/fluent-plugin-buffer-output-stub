FROM fluent/fluentd:v0.14.25-onbuild

COPY fluent-plugin-buffer-output-stub-0.0.1.gem /fluent-plugin-buffer-output-stub-0.0.1.gem

RUN apk add --update --virtual .build-deps \
        sudo build-base ruby-dev \
 && sudo gem install /fluent-plugin-buffer-output-stub-0.0.1.gem \
 && sudo chmod 644 /usr/lib/ruby/gems/2.*.0/gems/fluent-plugin-buffer-output-stub-0.0.1/lib/fluent/plugin/out_buffer_output_stub.rb \
 && sudo gem sources --clear-all \
 && apk del .build-deps \
 && rm -rf /var/cache/apk/* \
           /home/fluent/.gem/ruby/2.*.0/cache/*.gem
