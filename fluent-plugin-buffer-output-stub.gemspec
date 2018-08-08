Gem::Specification.new do |gem|
  gem.name          = 'fluent-plugin-buffer-output-stub'
  gem.description   = <<-eos
   Stubbed Fluentd buffered output plugin.
eos
  gem.summary       = 'fluentd stubbed buffered output plugin'
  gem.license       = 'Apache-2.0'
  gem.version       = '0.0.1'
  gem.authors       = ['Ling Huang']
  gem.email         = ['qingling128@qq.com']
  gem.required_ruby_version = Gem::Requirement.new('>= 2.3')

  gem.files         = Dir['**/*'].keep_if { |file| File.file?(file) }
  gem.test_files    = gem.files.grep(/^(test)/)
  gem.require_paths = ['lib']

  gem.add_runtime_dependency 'fluentd'
end
